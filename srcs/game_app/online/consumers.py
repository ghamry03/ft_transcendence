import json
import asyncio
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import UserApiUser, Tournament, Game, PlayerMatch
from django.utils import timezone
from asgiref.sync import sync_to_async

class RemotePlayerConsumer(AsyncWebsocketConsumer):

    PADDING = 20
    SPEED = 10
    paddleHScale = 0.2
    paddleWScale = 0.015
    queue = []
    players = {}
    update_lock = asyncio.Lock()
    logger = logging.getLogger(__name__)
    canvasHeight = 510
    canvasWidth = 960
    paddleHeight = canvasHeight * paddleHScale
    paddleWidth = canvasWidth * paddleWScale
    ballRadius = paddleWidth
    paddleSpeed = SPEED
    # canvasHeight = 580
    # canvasWidth = 1024

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
        self.logger.info("added new game info to db")
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
            self.logger.info("same user already in game or queue")
            await self.send(
                text_data=json.dumps({"type": "inGame"})
            )
        else:
            self.logger.info("player %s joined", self.player_id)
            queuedPlayerId = None
            async with self.update_lock:
                # search for a match in the queue
                if len(self.queue) > 0:
                    queuedPlayerId = self.queue[0]
                    self.logger.info("found a player %s with no opponent", queuedPlayerId)
                    gid = await self.createGame(queuedPlayerId, self.player_id)

                    # moving queued player from queue to player pool
                    self.queue.pop(0)
                    self.players[queuedPlayerId] = {
                        "id": queuedPlayerId,
                        "opponentId": self.player_id,
                        "paddlePosition":  self.canvasHeight / 2 - self.paddleHeight / 2,
                        "upPressed": False,
                        "downPressed": False,
                        "ready": False,
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
                        "paddlePosition": self.canvasHeight / 2 - self.paddleHeight / 2,
                        "upPressed": False,
                        "downPressed": False,
                        "ready": False,
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

            self.logger.info("queue len = %d", len(self.queue))

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
        
        if msg_type == "keypress":
            key = clientData.get("key")
            keyDown = clientData.get("keyDown")
            if key == "w":
                player["upPressed"] = keyDown
            elif key == "s":
                player["downPressed"] = keyDown

        elif msg_type == "ready":
            player["ready"] = True
            opponent = self.players[player["opponentId"]]
            if opponent["ready"] == True:                
                await asyncio.sleep(6)
                if playerId == player["groupOwner"]:
                    asyncio.create_task(self.game_loop(playerId, player["opponentId"]))
                else:
                    asyncio.create_task(self.game_loop(player["groupOwner"], playerId))

    async def state_update(self, event):
        # self.logger.info("sending a status update!!")
        await self.send(
            text_data=json.dumps(
                {
                    "type": "stateUpdate",
                    "leftPaddle": event["leftPaddle"],
                    "rightPaddle": event["rightPaddle"],
                    "leftScore": event["leftScore"],
                    "rightScore": event["rightScore"], 
                    "ballX": event["ballX"],
                    "ballY": event["ballY"],
                }
            )
        )
    
    async def matchFound(self, event):
        # self.logger.info("sending a status update!!")
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
        # self.logger.info("sending a status update!!")
        await self.send(
            text_data=json.dumps(
                {
                    "type": "disconnected",
                }
            )
        )

    async def game_loop(self, playerId1, playerId2):
        ballXaxis = self.canvasWidth / 2
        ballYaxis = self.canvasHeight / 2
        ballSpeedXaxis = self.SPEED
        ballSpeedYaxis = self.SPEED
        while playerId1 in self.players and playerId2 in self.players:
            async with self.update_lock:
                player1 = self.players[playerId1]
                player2 = self.players[playerId2]

                if player1["upPressed"] and player1["paddlePosition"] > self.PADDING:
                    player1["paddlePosition"] -= self.paddleSpeed
                elif player1["downPressed"] and player1["paddlePosition"] + self.paddleHeight < self.canvasHeight - self.PADDING:
                    player1["paddlePosition"] += self.paddleSpeed    
                if player2["upPressed"] and player2["paddlePosition"] > self.PADDING:
                    player2["paddlePosition"] -= self.paddleSpeed
                elif player2["downPressed"] and player2["paddlePosition"] + self.paddleHeight < self.canvasHeight - self.PADDING:
                    player2["paddlePosition"] += self.paddleSpeed    

                # ball pos calc - move to a sync function later
                ballXaxis += ballSpeedXaxis
                ballYaxis += ballSpeedYaxis

                # Top & bottom collision
                if ballYaxis - self.ballRadius < self.PADDING or ballYaxis + self.ballRadius > self.canvasHeight - self.PADDING:
                    ballSpeedYaxis = -ballSpeedYaxis

                # Left paddle collision
                if (
                    ballXaxis - self.ballRadius < self.paddleWidth
                    and player1["paddlePosition"] < ballYaxis < player1["paddlePosition"] + self.paddleHeight
                ):
                    ballSpeedXaxis = -ballSpeedXaxis

                # Right paddle collision
                if (
                    ballXaxis + self.ballRadius > self.canvasWidth - self.paddleWidth - self.PADDING
                    and player2["paddlePosition"] < ballYaxis < player2["paddlePosition"] + self.paddleHeight
                ):
                    ballSpeedXaxis = -ballSpeedXaxis

                # Check if ball goes out of bounds on left or right side of canvas
                if ballXaxis < 0:
                    player2["score"] += 1
                    ballXaxis = self.canvasWidth / 2;
                    ballYaxis = self.canvasHeight / 2;
                    ballSpeedXaxis = -ballSpeedXaxis
                    ballSpeedYaxis = -ballSpeedYaxis

                elif ballXaxis > self.canvasWidth - self.PADDING:
                    player1["score"] += 1
                    ballXaxis = self.canvasWidth / 2;
                    ballYaxis = self.canvasHeight / 2;
                    ballSpeedXaxis = -ballSpeedXaxis
                    ballSpeedYaxis = -ballSpeedYaxis

                await self.channel_layer.group_send(
                    playerId1,
                    { 
                        "type": "state_update", 
                        "leftPaddle": player1["paddlePosition"], 
                        "rightPaddle": player2["paddlePosition"],
                        "leftScore": player1["score"],
                        "rightScore": player2["score"], 
                        "ballX": ballXaxis, 
                        "ballY": ballYaxis 
                    },
                )
                if player1["score"] == 11 or player2["score"] == 11:
                    gid = player1["gid"]
                    score1 = player1["score"]
                    score2 = player2["score"]
                    await self.endGame(gid, playerId1, playerId2, score1, score2)
                    break
            await asyncio.sleep(0.05)
