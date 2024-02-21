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

    PLAYER_MAX = 8
    PADDING = 20
    SPEED = 13
    WIN_SCORE = 6
    update_lock = asyncio.Lock()
    logger = logging.getLogger(__name__)
    queue = PlayerQueue()
    players = {}
    tournaments = [] # list of group names of all active tournaments
    activeTournaments = {}

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
                    tourName = self.tournaments[-1]
                    playerUids, channelNames = self.queue.getCopy()
                    self.activeTournaments[tourName] = {
                        "tourName": tourName,
                        "playerUids": playerUids,
                        "channels": channelNames,
                    }
                    tid = await tour_db.createTournament()
                    self.logger.info("created tournament with id = %d", tid)
                    asyncio.create_task(self.runTournament(tourName, tid))
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
                player = self.players[self.playerId]
                opponent = self.players[player["opponentId"]]
                
                leftPos = player["playerPos"] if player["playerPos"] < opponent["playerPos"] else opponent["playerPos"]
                newPlayerPos = int((leftPos / 2) + self.PLAYER_MAX)
                requests.get('http://gameapp:2000/game/endGame/' 
                            + str(player['gid']) + '/' 
                            + str(player["id"]) + '/' 
                            + str(opponent["id"]) + '/'
                            + str(player["score"]) + '/'
                            + str(self.WIN_SCORE) + '/')
                self.logger.info("Ended game in db");
                await self.channel_layer.group_discard(
                    player["groupName"], self.channel_name
                )
                await self.channel_layer.group_discard(
                    player["tourName"], self.channel_name
                )
                await self.channel_layer.group_send(
                    player["tourName"], 
                    {
                        "type": "newPlayerJoined", 
                        "newPlayerId": opponent["id"],
                        "imgId": "player" + str(newPlayerPos)
                    }
                )
                await self.channel_layer.group_send(
                    player["groupName"],
                    {"type": "disconnected"}
                )
                await self.channel_layer.group_discard(
                    player["groupName"], player["channel"]
                )
                del self.players[self.playerId]
            else:
                await self.channel_layer.group_discard(
                    player["tourName"], self.channel_name
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
            if leftScore == self.WIN_SCORE or rightScore == self.WIN_SCORE:
                await self.channel_layer.group_send(
                    player["groupName"], 
                    {
                        "type": "matchEnded",
                        "leftScore": leftScore,
                        "rightScore": rightScore
                    }
                )
                self.logger.info("someone won with %d %d", leftScore, rightScore)
                leftPos = player["playerPos"] if player["playerPos"] < opponent["playerPos"] else opponent["playerPos"]
                # winnerId = player["id"] if player["score"] == self.WIN_SCORE else opponent["id"]
                winnerId = player["id"]
                newPlayerPos = int((leftPos / 2) + self.PLAYER_MAX)
                requests.get('http://gameapp:2000/game/endGame/' 
                            + str(player['gid']) + '/' 
                            + str(player["id"]) + '/' 
                            + str(opponent["id"]) + '/'
                            + str(player["score"]) + '/'
                            + str(opponent["score"]) + '/')
                self.logger.info("ended game in db");
                # await self.endGame( player['gid'], player["id"], opponent["id"], player["score"], opponent["score"])
                await self.channel_layer.group_discard(
                    player["groupName"], self.channel_name
                )
                await self.channel_layer.group_discard(
                    player["groupName"], opponent["channel"]
                )
                await self.channel_layer.group_send(
                    player["tourName"], 
                    {
                        "type": "newPlayerJoined", 
                        "newPlayerId": player["id"],
                        "imgId": "player" + str(newPlayerPos)
                    }
                )
                self.logger.info("sent winner info to client %d", player["id"]);
            else:
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
        
        elif msg_type == "playerReady":
            player["ready"] = True
            if opponent["ready"] == True:
                player["ready"] = False
                opponent["ready"] = False
                left = player["id"]
                right = opponent["id"]
                if player["playerPos"] > opponent["playerPos"]:
                    right = player["id"]
                    left = opponent["id"]                    
                await self.channel_layer.group_send(
                    player["groupName"],
                    {
                        "type": "roundStarting",
                        "roundNo": 1,
                        "leftPlayer": left, 
                        "rightPlayer": right,
                    },
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
    
    async def disconnected(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "disconnected",
                }
            )
        )

    async def matchEnded(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "matchEnded",
                    "leftScore": event["leftScore"],
                    "rightScore": event["rightScore"]
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

    async def runTournament(self, tourName, tid):
        playerUids = self.activeTournaments[tourName]["playerUids"]
        channels = self.activeTournaments[tourName]["channels"]

        self.logger.info("Starting tournament %s", tourName)
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
                "ready": False,
                "channel": channel1,
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
                "ready": False,
                "channel": channel2,
                "playerPos": i + 1,
            }
            self.logger.info("run tour players len = %d", len(self.players))
            # await self.channel_layer.group_send(
            #     groupName,
            #     {
            #         "type": "roundStarting",
            #         "roundNo": 1,
            #         "leftPlayer": pid1, 
            #         "rightPlayer": pid2,
            #     },
            # )
            # matches.append(asyncio.create_task(self.game_loop(pid1, pid2, groupName)))
        # round1Results = await asyncio.gather(*matches)
        # self.logger.info("round 1 results len = %d, type = %s", len(round1Results), type(round1Results))
        await self.channel_layer.group_send(
            tourName,
            {"type": "tournamentStarted", "playerList": playerUids},
        )


        
# round 2+ logic
        # fill 
        # send tournamentStarted event