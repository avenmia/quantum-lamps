import asyncio
import websockets
import json
import os
from enum import Enum

CONNECTION_OPEN = True
USERNAME = ""

class MessageType(Enum):
    Close = "Close"
    Closing = "Closing"
    Auth = "Auth"
    Input = "Input"
    Listening = "Listening"
    UserName = "UserName"

class Message:
    def __init__(self, message_type, payload):
        self.message_type = message_type
        self.payload = payload

def parseMessage(message):
    global CONNECTION_OPEN
    global USERNAME
    rec_message = Message(message['type'], message['payload'])
    print("Message type:",rec_message.message_type)
    print("Message payload:", rec_message.payload)
    if rec_message.message_type == "UserName":
        print("Now Listening")
        USERNAME = rec_message.payload
        print(USERNAME)
        send_message = json.dumps({'type': 'Listening', 'payload': 'Listening'})
        return send_message
    elif rec_message.message_type == MessageType.Input:
        print("Received input")
        #CONNECTION_OPEN = False
        send_message = json.dumps({'type': MessageType.Input, 'message': 'Received input'})
        CONNECTION_OPEN = False
        return send_message
    elif rec_message.message_type == MessageType.Closing:
        print("Close connection")
        send_message = json.dumps({'type': MessageType.Close, 'message': USERNAME})
        CONNECTION_OPEN = False
    elif rec_message.message_type == MessageType.Close:
        # Shouldn't get hit
        CONNECTION_OPEN = False
        return None

async def sendMessage(ws, message):
    await ws.send(message)
    server_message = json.loads(await ws.recv())
    message = parseMessage(server_message)

async def init_connection(message):
    print("Initial message:", message)
    global CONNECTION_OPEN
    uri = "ws://localhost:8081"
    async with websockets.connect(uri) as websocket:
        # send init message
        await websocket.send(message)
        while CONNECTION_OPEN:
            server_message = json.loads(await websocket.recv())
            message = parseMessage(server_message)
            await sendMessage(websocket, message)
            print("Message after parse:", message)
        await websocket.send(json.dumps({'type': MessageType.Close, 'message': USERNAME}))
        await websocket.close()
        #CONNECTION_OPEN = False
        #print("received message", json.load(message))

while CONNECTION_OPEN:
    SHARED_SECRET = os.environ['SHARED_SECRET']
    message = json.dumps({'type': "Auth", 'payload': {'username': 'Mike', 'secret': SHARED_SECRET}})
    asyncio.get_event_loop().run_until_complete(init_connection(message))