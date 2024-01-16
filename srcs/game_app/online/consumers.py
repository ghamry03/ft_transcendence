import json
import uuid
import asyncio
import math
import logging

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync

class RemotePlayerConsumer(AsyncWebsocketConsumer):

    SPEED = 10
    game_group_name = "game_group"
    queue = []
    players = {}
    update_lock = asyncio.Lock()
    logger = logging.getLogger(__name__)
    paddleHeight = 80
    paddleWidth = 10
    paddleSpeed = SPEED
    canvasHeight = 510
    canvasWidth = 960
    # canvasHeight = 580
    # canvasWidth = 1024

    async def connect(self):
        
        # self.player_id = str(uuid.uuid4())
        # self.logger.info("player %s connected to server", self.player_id)
        await self.accept()
        # await self.send(
        #     text_data=json.dumps({"type": "playerId", "playerId": self.player_id})
        # )
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
                    # if queuedPlayer["opponentId"] == None:
                    self.logger.info("found a player %s with no opponent", queuedPlayerId)

                    # moving queued player from queue to player pool
                    self.queue.pop(0)
                    self.players[queuedPlayerId] = {
                        "id": queuedPlayerId,
                        "opponentId": self.player_id,
                        "paddlePosition":  self.canvasHeight / 2 - self.paddleHeight / 2,
                        "upPressed": False,
                        "downPressed": False,
                        "ready": False,
                        "gid": queuedPlayerId
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
                        "gid": queuedPlayerId
                    }               
                    # asyncio.create_task(self.game_loop(queuedPlayerId, self.player_id))
                    await self.channel_layer.group_send(
                        queuedPlayerId,
                        {"type": "matchFound", "first": queuedPlayerId},
                    )
                else:
                    self.queue.append(self.player_id)
                    await self.channel_layer.group_add(
                        self.player_id, self.channel_name
                    )

            self.logger.info("queue len = %d", len(self.queue))


    async def disconnect(self, close_code):
        async with self.update_lock:
            if self.player_id in self.queue:
                self.queue.pop(self.queue.index(self.player_id))
            elif self.player_id in self.players:
                # if this player is in a match with another player, we want to let the them know that this player disconnected
                opponentId = self.players[self.player_id]["opponentId"]
                gid = self.players[self.player_id]["gid"]
                # if opponentId != None:
                #     self.players[opponentId]["opponentId"] = None
                del self.players[self.player_id]
                await self.channel_layer.group_discard(
                    self.player_id, self.channel_name
                )
                await self.channel_layer.group_send(
                    gid,
                    {"type": "disconnected"}
                )
                del self.players[opponentId]


    async def receive(self, text_data):
        text_data_json = json.loads(text_data)

        playerId = text_data_json.get("playerId")
        player = self.players.get(playerId, None)
        if not player:
            self.logger.info("not a player")
            return
        
        msg_type = text_data_json.get("type")
        if msg_type == "keypress":
            key = text_data_json.get("key")
            keyDown = text_data_json.get("keyDown")   
            if key == "w":
                player["upPressed"] = keyDown
            elif key == "s":
                player["downPressed"] = keyDown

        elif msg_type == "ready":
            player["ready"] = True
            opponent = self.players[player["opponentId"]]
            if opponent["ready"] == True:
                self.logger.info("both are ready!")
                if playerId == player["gid"]:
                    asyncio.create_task(self.game_loop(playerId, player["opponentId"]))
                else:
                    asyncio.create_task(self.game_loop(player["gid"], playerId))

            
    async def state_update(self, event):
        # self.logger.info("sending a status update!!")
        await self.send(
            text_data=json.dumps(
                {
                    "type": "stateUpdate",
                    "leftPaddle": event["leftPaddle"],
                    "rightPaddle": event["rightPaddle"],
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
                    "first": event["first"],
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
        ballRadius = 10
        ballSpeedXaxis = self.SPEED
        ballSpeedYaxis = self.SPEED
        while playerId1 in self.players and playerId2 in self.players:
            async with self.update_lock:
                player1 = self.players[playerId1]
                player2 = self.players[playerId2]

                if player1["upPressed"] and player1["paddlePosition"] > 0:
                    player1["paddlePosition"] -= self.paddleSpeed
                elif player1["downPressed"] and player1["paddlePosition"] + self.paddleHeight < self.canvasHeight:
                    player1["paddlePosition"] += self.paddleSpeed    
                if player2["upPressed"] and player2["paddlePosition"] > 0:
                    player2["paddlePosition"] -= self.paddleSpeed
                elif player2["downPressed"] and player2["paddlePosition"] + self.paddleHeight < self.canvasHeight:
                    player2["paddlePosition"] += self.paddleSpeed    

                # ball pos calc - move to a sync function later
                ballXaxis += ballSpeedXaxis
                ballYaxis += ballSpeedYaxis

                # Top & bottom collision
                if ballYaxis - ballRadius < 0 or ballYaxis + ballRadius > self.canvasHeight:
                    ballSpeedYaxis = -ballSpeedYaxis

                # Left paddle collision
                if (
                    ballXaxis - ballRadius < self.paddleWidth
                    and player1["paddlePosition"] < ballYaxis < player1["paddlePosition"] + self.paddleHeight
                ):
                    ballSpeedXaxis = -ballSpeedXaxis

                # Right paddle collision
                if (
                    ballXaxis + ballRadius > self.canvasWidth - self.paddleWidth
                    and player2["paddlePosition"] < ballYaxis < player2["paddlePosition"] + self.paddleHeight
                ):
                    ballSpeedXaxis = -ballSpeedXaxis

                # Check if ball goes out of bounds on left or right side of canvas
                if ballXaxis < 0:
                    # rightPlayerScore += 1
                    ballXaxis = self.canvasWidth / 2;
                    ballYaxis = self.canvasHeight / 2;

                elif ballXaxis > self.canvasWidth:
                    # leftPlayerScore += 1
                    ballXaxis = self.canvasWidth / 2;
                    ballYaxis = self.canvasHeight / 2;

                # if player1["updatePending"]:
                    # player1["updatePending"] = False
                await self.channel_layer.group_send(
                    playerId1,
                    { 
                        "type": "state_update", 
                        "leftPaddle": player1["paddlePosition"], 
                        "rightPaddle": player2["paddlePosition"], 
                        "ballX": ballXaxis, 
                        "ballY": ballYaxis 
                    },
                )
            await asyncio.sleep(0.05)
