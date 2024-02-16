from channels.generic.websocket import AsyncWebsocketConsumer
import json
import asyncio
import logging
import uuid
from . import tour_db
from .models import Tournament
import requests
from .PlayerQueue import PlayerQueue

class TournamentConsumer(AsyncWebsocketConsumer):

    PLAYER_MAX = 4
    PADDING = 20
    SPEED = 13
    update_lock = asyncio.Lock()
    logger = logging.getLogger(__name__)
    queue = PlayerQueue()
    players = {}
    tournaments = [] # list of group names of all active tournaments

	# Called when the websocket is handshaking as part of the connection process
    async def connect(self):
        await self.accept()
        self.playerId = int(self.scope['query_string'].decode('utf-8').split('=')[1])
        if self.queue.contains(self.playerId) or self.playerId in self.players: # or in an active tournament
            self.logger.info("Player %s is already in queue or a game", self.playerId)
            await self.send(
                text_data=json.dumps({"type": "inGame"})
            )
        else:
            async with self.update_lock:
                if self.queue.size() == 0:
                    self.tournaments.append(str(uuid.uuid4()))
                if self.queue.size() < self.PLAYER_MAX:
                    tourName = self.tournaments[-1]
                    # self.queue.append(self.playerId)
                    playerPos = self.queue.addPlayer(self.playerId, self.channel_name)
                    self.logger.info("Player %s joined", self.playerId)
                    self.logger.info("Queue len = %d", self.queue.size())
                    self.logger.info("Adding player to group %s", tourName)
                    # broadcast to queued players that a new player joined
                    await self.channel_layer.group_send(
                        tourName,
                        {
                            "type": "newPlayerJoined", 
                            "newPlayerId": self.playerId, 
                            "imgId": "player" + str(playerPos)
                        },
                    )
                    # send queued players info to new player
                    await self.send(
                        text_data=json.dumps({"type": "tournamentFound", "playerList": self.queue.getPlayers()})
                    )
                    # add new player to the queue group
                    await self.channel_layer.group_add(
                        tourName, self.channel_name
                    )
                    self.logger.info("channel name = %s", self.channel_name)
                if self.queue.size() == self.PLAYER_MAX:
                    playerUids, channelNames = self.queue.getCopy()
                    asyncio.create_task(self.runTournament(tourName, playerUids, channelNames))
                    self.queue.clear()

    # Called when the WebSocket closes for any reason
    async def disconnect(self, close_code):
        if close_code == 3001: 
            return 
        async with self.update_lock:
            if self.queue.contains(self.playerId):
                # self.queue.pop(self.queue.index(self.playerId))
                self.queue.removePlayer(self.playerId)
                await self.channel_layer.group_discard(
                    self.tournaments[-1], self.channel_name
                )
                # countPlayers = len(get_channel_layer().group_channels(self.tourName))
                if self.queue.size() > 0:
                    await self.channel_layer.group_send(
                        self.tournaments[-1],
                        {
                            "type": "playerLeftQueue",
                            "playerId": self.playerId,
                        }
                    )
                elif len(self.tournaments) > 0:
                    self.tournaments.pop()
            elif self.playerId in self.players:
                tourName = self.players[self.playerId]["tourName"]       
                groupName = self.players[self.playerId]["groupName"]       
                opponentId = self.players[self.playerId]["opponentId"]
                score1 = self.players[self.playerId]["score"]
                score2 = self.players[opponentId]["score"]
                gid = self.players[self.playerId]['gid']

                del self.players[self.playerId]
                del self.players[opponentId]
                await self.endGame(gid, self.playerId, opponentId, score1, score2)
                await self.channel_layer.group_discard(
                    self.playerId, self.channel_name
                )
                await self.channel_layer.group_send(
                    groupName,
                    {"type": "disconnected"}
                )

	# Called when the server receives a message from the WebSocket
    async def receive(self, text_data):
        clientData = json.loads(text_data)
        msg_type = clientData.get("type")

        playerId = int(clientData.get("playerId"))
        player = self.players.get(playerId, None)
        if not player:
            self.logger.info("not a player")
            return
        opponent = self.players[player["opponentId"]]
        if msg_type == "keypress":
            key = clientData.get("key")
            keyDown = clientData.get("keyDown")
            await self.channel_layer.group_send(
                player["groupName"],
                { 
                    "type": "keyUpdate",
                    "key": key,
                    "keyDown": keyDown,
                    "isLeft": player["playerPos"] < opponent["playerPos"],
                },
            )

        elif msg_type == "playerScored":
            player["score"] += 1
            leftScore = 0
            rightScore = 0
            ballDir = 1
            # left scored
            if player["playerPos"] < opponent["playerPos"]: # this player is the left
                leftScore = player["score"]
                rightScore = opponent["score"]
                ballDir = -1
            # right scored
            else:
                leftScore = opponent["score"]
                rightScore = player["score"]
            await self.channel_layer.group_send(
                player["groupName"], 
                {
                    "type": "scoreUpdate",
                    "leftScore": leftScore,
                    "rightScore": rightScore,
                    "ballDir": ballDir
                }
            )
            self.logger.info("Sent score update back %d %d", player["score"], opponent["score"])
        
        elif msg_type == "matchEnded":
            tourName = player["tourName"]       
            groupName = player["groupName"]       
            opponentId = player["opponentId"]
            score1 = player["score"]
            score2 = self.players[opponentId]["score"]
            gid = player['gid']

            del self.players[self.playerId]
            del self.players[opponentId]
            await self.endGame(gid, self.playerId, opponentId, score1, score2)
            await self.channel_layer.group_discard(
                self.playerId, self.channel_name
            )
    async def newPlayerJoined(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "newPlayerJoined",
                    "newPlayerId": event["newPlayerId"],
                    "imgId": event["imgId"],
                }
            )
        )
    
    async def playerLeftQueue(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "playerLeftQueue",
                    "playerId": event["playerId"],
                }
            )
        )
    
    async def tournamentStarted(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "tournamentStarted",
                    "playerList": event["playerList"],
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

    async def roundStarting(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "roundStarting",
                    "roundNo": event["roundNo"],
                    "leftPlayer": event["leftPlayer"],
                    "rightPlayer": event["rightPlayer"],
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

    
        # player {playerId, opponentId, gid, groupName, tid, score}
        # ---------------- SET UP ----------------
        # tid = create db record
        # add all players to players map while pairing them up
        # create db records for each of those matches and get the gids, store in players
        # create a channel group for each pair and save the group name
        # send "starting round 1" event for each pair with left and right positions

        # ---------------- START ----------------
        # for each pair, create_task for the game loop and store the returned task in the set
        # wait for the tasks in a loop with FIRST_COMPLETED, as long as there are pending 
        # for every task that finishes, update the scores in the db and broadcast the results to everyone
        # ...

    async def runTournament(self, tourName, playerUids, channels):
        self.logger.info("Starting tournament %s", tourName)
        await self.channel_layer.group_send(
            tourName,
            {"type": "tournamentStarted", "playerList": playerUids},
        )
        tid = await tour_db.createTournament()
        self.logger.info("created tournament with id = %d", tid)
        matches = []
        for i in range(0, self.PLAYER_MAX, 2):
            pid1 = playerUids[i]
            channel1 = channels[i]
            pid2 = playerUids[i + 1]
            channel2 = channels[i + 1]
            gameIdResponse = requests.get('http://gameapp:2000/game/createGame/' + str(pid1) + '/' + str(pid2) + '/' + str(tid) + '/')
            gid = int(gameIdResponse.text)
            groupName = str(pid1) + "_" + str(pid2)
            self.logger.info("creating group with name = %s, %s", groupName, type(groupName))
            await self.channel_layer.group_add(
                groupName, channel1
            )
            await self.channel_layer.group_add(
                groupName, channel2
            )
            self.players[pid1] = {
                "id": pid1,
                "opponentId": pid2,
                "tid": tid,
                "gid": gid,
                "groupName": groupName,
                "tourName": tourName,
                "score": 0,
                # "paddlePosition": self.canvasHeight / 2 - self.paddleHeight / 2,
                # "upPressed": False,
                # "downPressed": False,
                "playerPos": i,
            }
            self.players[pid2] = {
                "id": pid2,
                "opponentId": pid1,
                "tid": tid,
                "gid": gid,
                "groupName": groupName,
                "tourName": tourName,
                "score": 0,
                # "paddlePosition": self.canvasHeight / 2 - self.paddleHeight / 2,
                # "upPressed": False,
                # "downPressed": False,
                "playerPos": i + 1,
            }
            self.logger.info("run tour players len = %d", len(self.players))
            await self.channel_layer.group_send(
                groupName,
                {
                    "type": "roundStarting",
                    "roundNo": 1,
                    "leftPlayer": pid1, 
                    "rightPlayer": pid2,
                },
            )
            # matches.append(asyncio.create_task(self.game_loop(pid1, pid2, groupName)))
        # round1Results = await asyncio.gather(*matches)
        # self.logger.info("round 1 results len = %d, type = %s", len(round1Results), type(round1Results))


        
