import json
import uuid
import asyncio
import math
import logging

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync

class RemotePlayerConsumer(AsyncWebsocketConsumer):
    MAX_SPEED = 5
    THRUST = 0.2

    game_group_name = "game_group"
    players = {}
    update_lock = asyncio.Lock()
    logger = logging.getLogger(__name__)
    # connections = {}

    async def connect(self):
        # print("connected to server woohoo!!")
        self.player_id = str(uuid.uuid4())
        self.logger.info("player %s connected to server", self.player_id)
        await self.accept()

        await self.channel_layer.group_add(
            self.player_id, self.channel_name
        )

        await self.send(
            text_data=json.dumps({"type": "playerId", "playerId": self.player_id})
        )

        opponentId = None
        matchFound = False
        async with self.update_lock:
            # search for a match in the queue
            for queuedPlayer in self.players.values():
                if queuedPlayer["opponentId"] == None:
                    self.logger.info("found a player %s with no opponent", queuedPlayer["id"])
                    queuedPlayer["opponentId"] = self.player_id # assign new player to a player in the queue
                    opponentId = queuedPlayer["id"]
                    await self.channel_layer.group_send(
                        opponentId,
                        {"type": "matchStatus", "status": True, "playerDirection": 1},
                    )
                    matchFound = True
                    break
            self.players[self.player_id] = { # add new player to player pool
                "id": self.player_id,
                "opponentId": opponentId,
                "movingUp": False,
                "movingDown": False,
                "updatePending": False,
            }
            await self.send(
                text_data=json.dumps({"type": "matchStatus", "status": matchFound, "playerDirection": -1})
            )

        self.logger.info("count clients = %d", len(self.players))
        
        # if len(self.players) == 1:
        asyncio.create_task(self.game_loop(self.player_id))

    async def findMatch(self, newPlayerId):
        opponentId = None
        matchFound = False
        async with self.update_lock:
            # search for a match in the queue
            for queuedPlayer in self.players.values():
                if queuedPlayer["opponentId"] == None:
                    self.logger.info("found a player %s with no opponent", queuedPlayer["id"])
                    queuedPlayer["opponentId"] = newPlayerId # assign new player to a player in the queue
                    opponentId = queuedPlayer["id"]
                    await self.channel_layer.group_send(
                        opponentId,
                        {"type": "matchStatus", "status": True},
                    )
                    matchFound = True
                    break
            self.players[newPlayerId] = { # add new player to player pool
                "id": newPlayerId,
                "opponentId": opponentId,
                "movingUp": False,
                "movingDown": False,
                "updatePending": False,
            }
            await self.send(
                text_data=json.dumps({"type": "matchStatus", "status": matchFound})
            )

    async def disconnect(self, close_code):
        async with self.update_lock:
            if self.player_id in self.players:
                # if this player is in a match with another player, we want to let the them know that this player disconnected
                opponentId = self.players[self.player_id]["opponentId"]
                if opponentId != None:
                    self.players[opponentId]["opponentId"] = None
                del self.players[self.player_id]
        await self.channel_layer.group_discard(
            self.player_id, self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        key = text_data_json.get("key", "")
        keyDown = text_data_json.get("keyDown")
        player_id = text_data_json["playerId"]

        # self.logger.info("event from player %s", player_id)
        player = self.players.get(player_id, None)
        if not player:
            self.logger.info("not a player")
            return
        
        if key == "w":
            player["movingUp"] = keyDown
        elif key == "s":
            player["movingDown"] = keyDown
        player["updatePending"] = True

    async def state_update(self, event):
        # self.logger.info("sending a status update!!")
        await self.send(
            text_data=json.dumps(
                {
                    "type": "stateUpdate",
                    "objects": event["objects"],
                }
            )
        )
    
    async def matchStatus(self, event):
        # self.logger.info("sending a status update!!")
        await self.send(
            text_data=json.dumps(
                {
                    "type": "matchStatus",
                    "status": event["status"],
                    "playerDirection": event["playerDirection"],
                }
            )
        )

    async def game_loop(self, playerId):
        while playerId in self.players:
            async with self.update_lock:
                player = self.players[playerId]
                if player["opponentId"] != None: # player has an opponent 
                    if player["updatePending"]:
                        player["updatePending"] = False
                        await self.channel_layer.group_send(
                            player["opponentId"],
                            {"type": "state_update", "objects": player},
                            )
            await asyncio.sleep(0.05)
