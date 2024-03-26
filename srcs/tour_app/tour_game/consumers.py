from channels.generic.websocket import AsyncWebsocketConsumer
import json
import asyncio
import logging
import uuid
from . import tour_db
import requests
from .PlayerQueue import PlayerQueue

def getMaxPos(playerMax):
    maxPos = 0
    while playerMax > 1:
        maxPos += playerMax
        playerMax //= 2
    return maxPos

class TournamentConsumer(AsyncWebsocketConsumer):

    PLAYER_MAX = 2
    WIN_SCORE = 11
    update_lock = asyncio.Lock()
    logger = logging.getLogger(__name__)
    maxPos = getMaxPos(PLAYER_MAX)
    queue = PlayerQueue(maxPos)
    players = {}
    tournaments = [] # list of group names of all active tournaments
    activeTournaments = {}
    waitingPlayers = {}

	# Called when the websocket is handshaking as part of the connection process
    async def connect(self):
        await self.accept()
        self.playerId = int(self.scope['query_string'].decode('utf-8').split('=')[1])

        # Check if player is already in queue or in another active tournament in another session
        if self.queue.contains(self.playerId) or self.playerId in self.players or self.playerId in self.waitingPlayers:
            self.logger.info("Player %s is already in queue or a game", self.playerId)
            await self.send(
                text_data=json.dumps({"type": "inGame"})
            )
        else:
            async with self.update_lock:
                # If queue is empty, register a new tournament ID
                if self.queue.size() == 0:
                    self.tournaments.append(str(uuid.uuid4()))

                # If queue has not filled up yet
                if self.queue.size() < self.PLAYER_MAX:
                    tourName = self.tournaments[-1]
                    playerPos = self.queue.addPlayer(self.playerId, self.channel_name)
                    self.logger.info("Player %s joined", self.playerId)
                    self.logger.info("Queue len = %d", self.queue.size())
                    self.logger.info("Adding player to group %s", tourName)
                    # Broadcast to queued players that a new player joined
                    await self.channel_layer.group_send(
                        tourName,
                        {
                            "type": "newPlayerJoined", 
                            "newPlayerId": self.playerId, 
                            "imgId": str(playerPos)
                        },
                    )
                    # Send queued players info to new player
                    await self.send(
                        text_data=json.dumps({"type": "tournamentFound", "playerList": self.queue.getPlayers()})
                    )
                    # Add new player to the new tournament group
                    await self.channel_layer.group_add(
                        tourName, self.channel_name
                    )

                # If queue has filled up, start the tournament
                if self.queue.size() == self.PLAYER_MAX:
                    tourName = self.tournaments[-1]
                    playerUids, channelNames = self.queue.getCopy()
                    tid = await tour_db.createTournament()
                    self.logger.info("created tournament with id = %d", tid)
                    self.activeTournaments[tourName] = {
                        "tourName": tourName,
                        "tid": tid,
                        "playerUids": playerUids,
                        "channels": channelNames,
                        "countReady": self.PLAYER_MAX,
                        "countPlayers": self.PLAYER_MAX,
                        "curRank": self.PLAYER_MAX,
                        "start": 0,
                        "end": self.PLAYER_MAX,
                    }
                    asyncio.create_task(self.startRound(tourName))
                    self.queue.clear()

    # Called when the WebSocket closes for any reason
    async def disconnect(self, close_code):
        if close_code == 3001: 
            return 
        async with self.update_lock:

            # If player is in queue
            if self.queue.contains(self.playerId):
                self.logger.info("Player %d left queue", self.playerId)
                self.queue.removePlayer(self.playerId)
                await self.channel_layer.group_discard(
                    self.tournaments[-1], self.channel_name
                )
                if self.queue.size() > 0:
                    # Broadcast to other players in queue that someone left
                    await self.channel_layer.group_send(
                        self.tournaments[-1],
                        {
                            "type": "playerLeftQueue",
                            "playerId": self.playerId,
                        }
                    )
                elif len(self.tournaments) > 0:
                    self.tournaments.pop()

            # If player is in an active game in a tournament
            elif self.playerId in self.players:
                self.logger.info("Player %d disconnected during a match", self.playerId)
                player = self.players[self.playerId]
                opponent = self.players[player["opponentId"]]
                tour = self.activeTournaments.get(player["tourName"], None)

                # Clearing disconnected player's channel from all groups
                await self.channel_layer.group_discard(
                    player["groupName"], self.channel_name
                )
                await self.channel_layer.group_discard(
                    player["tourName"], self.channel_name
                )

                # Let the other player know that their opponent disconnected
                await self.channel_layer.group_send(
                    player["groupName"],
                    {"type": "disconnected"}
                )
                await self.channel_layer.group_discard(
                    player["groupName"], opponent["channel"]
                )

                # End the round 
                opponent["score"] = self.WIN_SCORE
                await self.endRound(opponent, player)
                if tour:
                    if tour["countReady"] == tour["countPlayers"]:
                        asyncio.create_task(self.startRound(tour["tourName"]))

            # If the player is in an active tournament but not in a match
            elif self.playerId in self.waitingPlayers:
                self.logger.info("Player %d disconnected while waiting for next match", self.playerId)
                waitingPlayer = self.waitingPlayers[self.playerId]
                tourName = waitingPlayer["tourName"]
                playerPos = waitingPlayer["bracketPos"]
                tour = self.activeTournaments.get(waitingPlayer["tourName"], None)
                if tour:
                    tour["channels"][playerPos] = None
                # Remove player from the tournament channel group
                await self.channel_layer.group_discard(
                    tourName, self.channel_name
                )
                del self.waitingPlayers[self.playerId]

    # This function ends a round, closes the tournament if its the last round, does all final db writes 
    async def endRound(self, winner, loser):
        self.logger.info("Ending round")
        
        # Save game results to db
        requests.get('http://gameapp:8003/game/endGame/' 
                    + str(winner['gid']) + '/' 
                    + str(winner["id"]) + '/' 
                    + str(loser["id"]) + '/'
                    + str(winner["score"]) + '/'
                    + str(loser["score"]) + '/')
        
        # Update the rank of the loser in this match
        tour = self.activeTournaments[winner["tourName"]]
        await tour_db.updateRank(loser['tid'], loser['id'], tour['curRank'])
        tour["curRank"] -= 1

        # End the tournament here and cleanup if this is the last round
        if tour["curRank"] == 1:
            self.logger.info("Last match ended, Tournament ending")
            await self.channel_layer.group_send(
                winner["tourName"], 
                {
                    "type": "tournamentEnded", 
                    "winnerId": winner["id"]
                }
            )
            # Update the rank of the winner in this match
            await tour_db.updateRank(winner['tid'], winner['id'], tour['curRank'])
            tour["curRank"] -= 1
            await tour_db.endTournament(winner["tid"])
            del self.activeTournaments[winner["tourName"]]

        # Find winner's new position on the bracket and broadcast to tournament for the next round
        else:
            leftPos = winner["playerPos"] if winner["playerPos"] < loser["playerPos"] else loser["playerPos"]
            newPlayerPos = (leftPos // 2) + self.PLAYER_MAX
            await self.channel_layer.group_send(
                winner["tourName"], 
                {
                    "type": "newPlayerJoined", 
                    "newPlayerId": winner["id"],
                    "imgId": str(newPlayerPos)
                }
            )
            
            # Add winner info to tournament in prep for next round
            tour["playerUids"][newPlayerPos] = winner["id"]
            tour["channels"][newPlayerPos] = winner["channel"]
            tour["countReady"] += 1
            
            # Add winner to waitingPlayer pool
            self.waitingPlayers[winner["id"]] = {
                "id": winner["id"],
                "channel": winner["channel"],
                "tourName": winner["tourName"],
                "bracketPos": newPlayerPos,
            }
        # Remove both players from active player pool
        del self.players[winner["id"]]
        del self.players[loser["id"]]

	# Called when the server receives a message from the WebSocket
    async def receive(self, text_data):
        clientData = json.loads(text_data)
        msg_type = clientData.get("type")

        playerId = int(clientData.get("playerId"))
        player = self.players.get(playerId, None)
        # Ensuring that they are an active player
        if not player:
            self.logger.info("Not an active player")
            return
        opponent = self.players[player["opponentId"]]

        # Received a keypress event from one of the players
        if msg_type == "keypress":
            key = clientData.get("key")
            keyDown = clientData.get("keyDown")
            # Forward the key press event to both players so the paddle will move on their ends
            await self.channel_layer.group_send(
                player["groupName"],
                { 
                    "type": "keyUpdate",
                    "key": key,
                    "keyDown": keyDown,
                    "isLeft": player["playerPos"] < opponent["playerPos"], # Checks if its the left player
                },
            )

        # A player has scored
        elif msg_type == "playerScored":
            player["score"] += 1
            leftScore = 0
            rightScore = 0
            ballDir = 1
            # Left player scored
            if player["playerPos"] < opponent["playerPos"]: # checking if this player is the left
                leftScore = player["score"]
                rightScore = opponent["score"]
                ballDir = -1
            # Right player scored
            else:
                leftScore = opponent["score"]
                rightScore = player["score"]

            # If this was the winning score, end the game
            if leftScore == self.WIN_SCORE or rightScore == self.WIN_SCORE:
                # Broadcast match end message with final scores
                await self.channel_layer.group_send(
                    player["groupName"], 
                    {
                        "type": "matchEnded",
                        "leftScore": leftScore,
                        "rightScore": rightScore
                    }
                )
                # Clear both players channels from their group
                await self.channel_layer.group_discard(
                    player["groupName"], self.channel_name
                )
                await self.channel_layer.group_discard(
                    player["groupName"], opponent["channel"]
                )
                # End the round for these players
                tour = self.activeTournaments[player["tourName"]]
                await self.endRound(player, opponent)
                # Start the next round if this was the last match in the round
                if tour["countReady"] == tour["countPlayers"]:
                    asyncio.create_task(self.startRound(tour["tourName"]))
            # Forward the new scores to both players and continue the game
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
        
        # Player is ready to start their assigned match
        elif msg_type == "playerReady":
            player["ready"] = True
            # Check if their opponent is also ready
            if opponent["ready"] == True:
                player["ready"] = False
                opponent["ready"] = False
                # Find who the left and right players are
                left = player["id"]
                right = opponent["id"]
                if player["playerPos"] > opponent["playerPos"]:
                    right = player["id"]
                    left = opponent["id"]
                # Send player positions to both players
                await self.channel_layer.group_send(
                    player["groupName"],
                    {
                        "type": "roundStarting",
                        "leftPlayer": left, 
                        "rightPlayer": right,
                    },
                )

        elif msg_type == "gameReady":
            player["ready"] = True
            # Check if their opponent is also ready
            if opponent["ready"] == True:
                player["ready"] = False
                opponent["ready"] = False
                await self.channel_layer.group_send(
                    player["groupName"],
                    {
                        "type": "gameReady",
                    },
                )

    # Call this to start a new round of a tournament, giving it the tournament ID
    # This function would also end the tournament if it finds there aren't enough people to continue
    async def startRound(self, tourName):
        tour = self.activeTournaments[tourName]
        playerUids = tour["playerUids"]
        channels = tour["channels"]
        tid = tour["tid"]
        canceled = False 
    
        self.logger.info("Starting round %s", tourName)
        # While there are enough players ready to start a new round
        while tour["countReady"] == tour["countPlayers"]:
            self.logger.info("setting up round for %d %d ", tour["start"], tour["end"])

            tour["countReady"] = 0
            tour["countPlayers"] //= 2
            # Go through list of all players eligible for next round
            # The indices of these players' ids are within the range of tour["start"] to tour["end"],
            # This range is updated after every round
            for i in range(tour["start"], tour["end"], 2):
                if playerUids[i] == 0:
                    continue
                
                pid1 = playerUids[i]
                pid2 = playerUids[i + 1]

                channel1 = channels[i]
                channel2 = channels[i + 1]

                # Checking if the players left while waiting for the round to start
                # If both players left, we cancel the tournament because there aren't enough people to continue
                if not channel1 and not channel2:
                    canceled = True
                    break

                # Register the new game in the db and create new channel group for the match
                gameIdResponse = requests.get('http://gameapp:8003/game/createGame/' + str(pid1) + '/' + str(pid2) + '/' + str(tid) + '/')
                gid = int(gameIdResponse.text)
                groupName = str(pid1) + "_" + str(pid2)
                
                # Remove the players from the waiting player pool
                if pid1 in self.waitingPlayers: 
                    del self.waitingPlayers[pid1]
                if pid2 in self.waitingPlayers:
                    del self.waitingPlayers[pid2]
                
                # Adding the players to the active player pool
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

                # If one of the players left while waiting for the match to be ready,
                # We automatically assign the one who stayed to be the winner
                if not channel2:
                    self.players[pid1]["score"] = self.WIN_SCORE
                    await self.endRound(self.players[pid1], self.players[pid2])
                elif not channel1:
                    self.players[pid2]["score"] = self.WIN_SCORE
                    await self.endRound(self.players[pid2], self.players[pid1])

                # If both players are still online, we add them to the same channel group 
                if channel1 and channel2:
                    self.logger.info("Creating group with name = %s", groupName)
                    await self.channel_layer.group_add(
                        groupName, channel1
                    )
                    await self.channel_layer.group_add(
                        groupName, channel2
                    )
            # Reset the tournament start and end ranges for the next round
            tour["start"] = tour["end"]
            tour["end"] = tour["end"] + tour["countPlayers"]
            if canceled:
                break
        
        # Broadcast to remaining players that the tournament was cancelled 
        if canceled:
            await self.channel_layer.group_send(
                tourName,
                {"type": "tournamentCanceled"},
            )
            await tour_db.deleteTournament(tid)
            del self.activeTournaments[tourName]
        # Broadcast to all players that the next round is starting
        else:
            await self.channel_layer.group_send(
                tourName,
                {"type": "tournamentStarted"},
            )

    # ------------- All handlers for the broadcast messages sent by the server -------------

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
    
    async def tournamentEnded(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "tournamentEnded",
                    "winnerId": event["winnerId"],
                }
            )
        )
    
    async def tournamentCanceled(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "tournamentCanceled",
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
                }
            )
        )
    
    async def gameReady(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "gameReady",
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