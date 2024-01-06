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

    game_rooms = {}

    async def connect(self):
        # print("connected to server woohoo!!")
        self.player_id = str(uuid.uuid4())
        self.logger.info("player %s connected to server, %s", self.player_id, self.channel_name)
        await self.accept()

        await self.channel_layer.group_add(
            self.game_group_name, self.channel_name
        )

        await self.send(
            text_data=json.dumps({"type": "playerId", "playerId": self.player_id})
        )

        async with self.update_lock:
            self.players[self.player_id] = {
                "id": self.player_id,
                "x": 500,
                "y": 500,
                "facing": 0,
                "dx": 0,
                "dy": 0,
                "thrusting": False,
                "movingDown": False,
                "movingUp": False,
            }

        self.logger.info("count clients = %d", len(self.players))
        if len(self.players) == 1:
            asyncio.create_task(self.game_loop())

    async def disconnect(self, close_code):
        async with self.update_lock:
            if self.player_id in self.players:
                del self.players[self.player_id]

        await self.channel_layer.group_discard(
            self.game_group_name, self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get("type", "")

        player_id = text_data_json["playerId"]

        player = self.players.get(player_id, None)
        if not player:
            self.logger.info("not a player")
            return
        
        if message_type == "w":
            self.logger.info("w pressed!")
        elif message_type == "s":
            self.logger.info("s pressed!")
        elif message_type == "ArrowUp":
            self.logger.info("ArrowUp pressed!")
            player["movingDown"] = True
        elif message_type == "ArrowDown":
            self.logger.info("ArrowDown pressed!")
        # elif message_type == "mouseDown":
        #     player["thrusting"] = True
        # elif message_type == "mouseUp":
        #     player["thrusting"] = False
        # elif message_type == "facing":
        #     player["facing"] = text_data_json["facing"]

    async def state_update(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "stateUpdate",
                    "objects": event["objects"],
                }
            )
        )

    def create_game_room(self, pair_identifier):
        # Create a group for the pair
        game_id = f"game_{pair_identifier}"
        asyncio.create_task(self.channel_layer.group_add(game_id, self.channel_name))
    
    async def add_to_pair(self, pair_identifier):
        if pair_identifier in self.pairs:
            # Add the channel to an existing pair
            self.pairs[pair_identifier].append(self.channel_name)
        else:
            # Create a new pair and add the channel
            self.pairs[pair_identifier] = [self.channel_name]

    async def game_loop(self):
        while len(self.players) > 0:
            async with self.update_lock:
                for player in self.players.values():
                    if player["thrusting"]:
                        dx = self.THRUST * math.cos(player["facing"])
                        dy = self.THRUST * math.sin(player["facing"])
                        player["dx"] += dx
                        player["dy"] += dy

                        speed = math.sqrt(player["dx"] ** 2 + player["dy"] ** 2)
                        if speed > self.MAX_SPEED:
                            ratio = self.MAX_SPEED / speed
                            player["dx"] *= ratio
                            player["dy"] *= ratio

                    player["x"] += player["dx"]
                    player["y"] += player["dy"]

            await self.channel_layer.group_send(
                self.game_group_name,
                {"type": "state_update", "objects": list(self.players.values())},
            )
            await asyncio.sleep(0.05)