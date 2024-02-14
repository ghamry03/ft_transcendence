import json
import asyncio
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import UserApiUser, Game, PlayerMatch
from django.utils import timezone
from asgiref.sync import sync_to_async

class RemotePlayerConsumer(AsyncWebsocketConsumer):

    queue = []
    players = {}
    update_lock = asyncio.Lock()
    logger = logging.getLogger(__name__)

    @sync_to_async
    def createGame(self, pid1, pid2):
        game = Game.objects.create(
            starttime=timezone.now()
        )
        player1 = UserApiUser.objects.get(uid=int(pid1))
        PlayerMatch.objects.create(
            game=game,
            player=player1,
            score=0
        )
        player2 = UserApiUser.objects.get(uid=int(pid2))
        PlayerMatch.objects.create(
            game=game,
            player=player2,
            score=0
        )
        self.logger.info("Created new game record in database")
        return game.id
    
    @sync_to_async
    def endGame(self, gid, pid1, pid2, score1, score2):
        game = Game.objects.get(id=int(gid))
        game.endtime = timezone.now()
        game.save()

        player1 = PlayerMatch.objects.get(game=gid, player=pid1)
        player1.score = score1
        player1.save()

        player2 = PlayerMatch.objects.get(game=gid, player=pid2)
        player2.score = score2
        player2.save()
        self.logger.info("game with gid %d ended", gid)

    async def connect(self):
        
        await self.accept()
        self.player_id = self.scope['query_string'].decode('utf-8').split('=')[1]
        if self.player_id in self.queue or self.player_id in self.players:
            self.logger.info("Same user already in game or queue")
            await self.send(
                text_data=json.dumps({"type": "inGame"})
            )
        else:
            self.logger.info("Player %s joined", self.player_id)
            queuedPlayerId = None
            async with self.update_lock:
                # search for a match in the queue
                if len(self.queue) > 0:
                    queuedPlayerId = self.queue[0]
                    self.logger.info("Found a player %s with no opponent", queuedPlayerId)
                    gid = await self.createGame(queuedPlayerId, self.player_id)

                    # moving queued player from queue to player pool
                    self.queue.pop(0)
                    self.players[queuedPlayerId] = {
                        "id": queuedPlayerId,
                        "opponentId": self.player_id,
                        "score": 0,
                        "groupOwner": queuedPlayerId,
                        "gid": gid
                    }
                    
                    # adding new player to the opponent's group
                    await self.channel_layer.group_add(
                        queuedPlayerId, self.channel_name
                    )

                    # adding new player to player pool
                    self.players[self.player_id] = { # add new player to player pool
                        "id": self.player_id,
                        "opponentId": queuedPlayerId,
                        "score": 0,
                        "groupOwner": queuedPlayerId,
                        "gid": gid
                    }               
                    # asyncio.create_task(self.game_loop(queuedPlayerId, self.player_id))
                    await self.channel_layer.group_send(
                        queuedPlayerId,
                        {"type": "matchFound", "left": int(queuedPlayerId), "right": int(self.player_id)},
                    )
                else:
                    self.queue.append(self.player_id)
                    await self.channel_layer.group_add(
                        self.player_id, self.channel_name
                    )

            self.logger.info("Queue len = %d", len(self.queue))

    async def disconnect(self, close_code=None):
        # this is a check for duplicate tab we so dont disconnect the other tab
        if close_code == 3001: 
            return 
        async with self.update_lock:
            if self.player_id in self.queue:
                self.queue.pop(self.queue.index(self.player_id))
            elif self.player_id in self.players:
                # if this player is in a match with another player, we want to let the them know that this player disconnected
                groupOwner = self.players[self.player_id]["groupOwner"]
                opponentId = self.players[self.player_id]["opponentId"]
                score1 = self.players[self.player_id]["score"]
                score2 = self.players[opponentId]["score"]
                gid = self.players[self.player_id]['gid']

                del self.players[self.player_id]
                await self.channel_layer.group_discard(
                    self.player_id, self.channel_name
                )
                await self.channel_layer.group_send(
                    groupOwner,
                    {"type": "disconnected"}
                )
                del self.players[opponentId]
                await self.endGame(gid, self.player_id, opponentId, score1, score2)


    async def receive(self, text_data):
        clientData = json.loads(text_data)
        msg_type = clientData.get("type")

        playerId = clientData.get("playerId")
        player = self.players.get(playerId, None)
        if not player:
            self.logger.info("not a player")
            return
        opponent = self.players[player["opponentId"]]
        if msg_type == "keypress":
            key = clientData.get("key")
            keyDown = clientData.get("keyDown")
            await self.channel_layer.group_send(
                player["groupOwner"],
                { 
                    "type": "keyUpdate",
                    "key": key,
                    "keyDown": keyDown,
                    "isLeft": playerId == player["groupOwner"],
                },
            )

        elif msg_type == "playerScored":
            player["score"] += 1
            leftScore = 0
            rightScore = 0
            ballDir = 1
            # left scored
            if playerId == player["groupOwner"]: # this player is the left
                leftScore = player["score"]
                rightScore = opponent["score"]
                ballDir = -1
            # right scored
            else:
                leftScore = opponent["score"]
                rightScore = player["score"]
            await self.channel_layer.group_send(
                player["groupOwner"], 
                {
                    "type": "scoreUpdate",
                    "leftScore": leftScore,
                    "rightScore": rightScore,
                    "ballDir": ballDir
                }
            )
            self.logger.info("Sent score update back %d %d", player["score"], opponent["score"])
    
    async def matchFound(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "matchFound",
                    "left": event["left"],
                    "right": event["right"],
                }
            )
        )
    
    async def disconnected(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "disconnected",
                }
            )
        )
    
    async def scoreUpdate(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "scoreUpdate",
                    "leftScore": event["leftScore"],
                    "rightScore": event["rightScore"],
                    "ballDir": event["ballDir"]
                }
            )
        )
    
    async def keyUpdate(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "keyUpdate",
                    "key": event["key"],
                    "keyDown": event["keyDown"],
                    "isLeft": event["isLeft"],
                }
            )
        )
