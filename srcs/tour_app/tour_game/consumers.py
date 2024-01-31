from channels.generic.websocket import AsyncWebsocketConsumer
# from channels.asgi import get_channel_layer
import json
import asyncio
import logging
import uuid
from .models import Tournament
from django.utils import timezone
import requests
from asgiref.sync import sync_to_async
from .PlayerQueue import PlayerQueue

class TournamentConsumer(AsyncWebsocketConsumer):

    update_lock = asyncio.Lock()
    logger = logging.getLogger(__name__)
    # queue = [0 for i in range(8)] 
    queue = PlayerQueue()
    players = {}
    tournaments = [] # list of group names of all active tournaments

    # @sync_to_async
    # def addToQueue(self, playerId):
    #     for idx, a in enumerate(self.queue):
    #         if self.queue[idx] == 0:
    #             self.queue[idx] = playerId
        
    
	# Called when the websocket is handshaking as part of the connection process
    async def connect(self):
        await self.accept()
        self.playerId = int(self.scope['query_string'].decode('utf-8').split('=')[1])
        self.logger.info("created queue with len = %d", self.queue.size())
        if self.queue.contains(self.playerId) or self.playerId in self.players: # or in an active tournament
            self.logger.info("Player %s is already in queue or a game", self.playerId)
            await self.send(
                text_data=json.dumps({"type": "inGame"})
            )
        else:
            async with self.update_lock:
                if self.queue.size() == 0:
                    self.tournaments.append(str(uuid.uuid4()))
                if self.queue.size() < 8:
                    tourName = self.tournaments[-1]
                    # self.queue.append(self.playerId)
                    playerPos = self.queue.addPlayer(self.playerId)
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
                if self.queue.size() == 8:
                    playerList = self.queue.getCopy()
                    asyncio.create_task(self.runTournament(tourName, playerList))
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
            elif self.playerId in self.players:
                tourGroupName = self.players[self.playerId]["groupName"]
                del self.players[self.playerId]
                # send it to the match instead of the whole tournament
                # await self.channel_layer.group_send(
                #         tourGroupName,
                #         {
                #             "type": "playerLeftQueue",
                #             "playerId": self.playerId,
                #         }
                #     )

	# Called when the server receives a message from the WebSocket
    async def receive(self, text_data):
        await self.send(text_data=json.dumps({'message': text_data}))

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

    async def runTournament(self, tourName, playerList):
        self.logger.info("Starting tournament %s", tourName)
        for uid in playerList:
            playerName = requests.get('http://userapp:3000/users/api/testing/' + str(uid))
            self.logger.info(playerName.content)
        await self.channel_layer.group_send(
            tourName,
            {"type": "tournamentStarted", "playerList": playerList},
        )
