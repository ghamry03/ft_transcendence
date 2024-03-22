import json
import asyncio
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from . import game_db

class RemotePlayerConsumer(AsyncWebsocketConsumer):

    queue = []
    players = {}
    update_lock = asyncio.Lock()
    logger = logging.getLogger(__name__)
    WIN_SCORE = 6

	# Called when the websocket is handshaking as part of the connection process
    async def connect(self):
        
        await self.accept()
        self.player_id = self.scope['query_string'].decode('utf-8').split('=')[1]

        # Check if player is already in queue or in another active tournament in another session
        if self.player_id in self.queue or self.player_id in self.players:
            self.logger.info("Same user already in game or queue")
            await self.send(
                text_data=json.dumps({"type": "inGame"})
            )
        else:
            self.logger.info("Player %s joined", self.player_id)
            queuedPlayerId = None
            async with self.update_lock:
                # Search for a match in the queue
                if len(self.queue) > 0:
                    queuedPlayerId = self.queue[0]
                    self.logger.info("Found a player %s with no opponent", queuedPlayerId)
                    gid = await game_db.createGame(queuedPlayerId, self.player_id)

                    # Moving queued player from queue to player pool
                    self.queue.pop(0)
                    self.players[queuedPlayerId] = {
                        "id": queuedPlayerId,
                        "opponentId": self.player_id,
                        "score": 0,
                        "groupOwner": queuedPlayerId,
                        "gid": gid
                    }
                    
                    # Adding new player to the opponent's group
                    await self.channel_layer.group_add(
                        queuedPlayerId, self.channel_name
                    )

                    # Adding new player to player pool
                    self.players[self.player_id] = { # add new player to player pool
                        "id": self.player_id,
                        "opponentId": queuedPlayerId,
                        "score": 0,
                        "groupOwner": queuedPlayerId,
                        "gid": gid
                    }

                    # Broadcast to both players that match has been found
                    await self.channel_layer.group_send(
                        queuedPlayerId,
                        {"type": "matchFound", "left": int(queuedPlayerId), "right": int(self.player_id)},
                    )
                else:
                    # Add the player to queue
                    self.queue.append(self.player_id)
                    await self.channel_layer.group_add(
                        self.player_id, self.channel_name
                    )
            self.logger.info("Queue len = %d", len(self.queue))

    # Called when the WebSocket closes for any reason
    async def disconnect(self, close_code=None):
        # This is a check for duplicate tab we so dont disconnect the other tab
        if close_code == 3001: 
            return 
        async with self.update_lock:
            # If player is in queue
            if self.player_id in self.queue:
                self.queue.pop(self.queue.index(self.player_id))
            # If player is in an active game
            elif self.player_id in self.players:
                self.logger.info("Player %d disconnected during a match", self.player_id)
                groupOwner = self.players[self.player_id]["groupOwner"]
                opponentId = self.players[self.player_id]["opponentId"]
                if opponentId == None:
                    await self.channel_layer.group_discard(
                        groupOwner, self.channel_name
                    )
                    del self.players[self.player_id]
                else:
                    # if this player is in a match with another player, we want to let the them know that this player disconnected
                    score1 = self.players[self.player_id]["score"]
                    gid = self.players[self.player_id]['gid']

                    del self.players[self.player_id]
                    await self.channel_layer.group_discard(
                        groupOwner, self.channel_name
                    )
                    await self.channel_layer.group_send(
                        groupOwner,
                        {"type": "disconnected"}
                    )
                    del self.players[opponentId]
                    await game_db.endGame(gid, self.player_id, opponentId, score1, self.WIN_SCORE)

	# Called when the server receives a message from the WebSocket
    async def receive(self, text_data):
        clientData = json.loads(text_data)
        msg_type = clientData.get("type")

        playerId = clientData.get("playerId")
        player = self.players.get(playerId, None)
        # Ensuring that they are an active player
        if not player:
            self.logger.info("not a player")
            return
        opponent = self.players[player["opponentId"]]
        # Received a keypress event from one of the players
        if msg_type == "keypress":
            key = clientData.get("key")
            keyDown = clientData.get("keyDown")
            # Forward the key press event to both players so the paddle will move on their ends
            await self.channel_layer.group_send(
                player["groupOwner"],
                { 
                    "type": "keyUpdate",
                    "key": key,
                    "keyDown": keyDown,
                    "isLeft": playerId == player["groupOwner"],
                },
            )
        # A player has scored
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

            if leftScore == self.WIN_SCORE or rightScore == self.WIN_SCORE:
                # Broadcast match end message with final scores
                await self.channel_layer.group_send(
                    player["groupOwner"], 
                    {
                        "type": "matchEnded",
                        "leftScore": leftScore,
                        "rightScore": rightScore
                    }
                )

                # Clear both players channels from their group
                await self.channel_layer.group_discard(
                    player["groupOwner"], self.channel_name
                )
                # Update game ending info in the db
                await game_db.endGame(player["gid"], self.player_id, opponent["id"], player["score"], opponent["score"])
                opponentId = self.players[self.player_id]["opponentId"]
                self.players[opponentId]["opponentId"] = None
                del self.players[self.player_id]
                self.logger.info("Match ended %d %d", player["score"], opponent["score"])
            # Forward the new scores to both players and continue the game
            else:
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
    
    # ------------- All handlers for the broadcast messages sent by the server -------------
    
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