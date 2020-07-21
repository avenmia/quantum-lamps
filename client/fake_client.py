import websockets
import asyncio
import json
import os
from enum import Enum


from dotenv import load_dotenv
load_dotenv()
SHARED_SECRET = os.environ['SHARED_SECRET']
WS_URI = os.environ['WS_URI']


# WebSocket Code #
class MessageType(Enum):
    Close = 1
    Closing = 2
    Auth = 3
    Input = 4
    Listening = 5
    Username = 6


async def handleMessages(ws, message):
    await ws.send(message)


async def init_connection(message):
    global WS_URI
    uri = WS_URI
    async with websockets.connect(uri) as websocket:
        await websocket.send(message)
        print("Connection is open")
        is_connected = True
        while is_connected:
            # read input send message
            x = input("Num1:")
            y = input("Num2:")
            z = input("Num3:")
            user_msg = json.dumps({'type': 'Input', 'payload': [x, y, z]})
            await handleMessages(websocket, user_msg)
    await websocket.send(json.dumps({'type': MessageType.Close.name, 'message': 'Frank'}))
    await websocket.close()


async def main():
    message = json.dumps({'type': "Auth", 'payload': {
        'username': 'Frank', 'secret': SHARED_SECRET}})
    await init_connection(message)


asyncio.run(main())
