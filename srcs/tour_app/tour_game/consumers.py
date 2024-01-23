from channels.generic.websocket import AsyncWebsocketConsumer
import json
import asyncio
import logging

class TournamentConsumer(AsyncWebsocketConsumer):
	# Called when the websocket is handshaking as part of the connection process
    async def connect(self):
        await self.accept()

	# Called when the WebSocket closes for any reason
    async def disconnect(self, close_code):
        pass

	# Called when the server receives a message from the WebSocket
    async def receive(self, text_data):
        await self.send(text_data=json.dumps({'message': text_data}))
