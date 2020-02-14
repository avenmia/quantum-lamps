import asyncio
import websockets
import json
from enum import IntEnum

CONNECTION_OPEN = True

class MessageType(IntEnum):
    Close = 0
    Init = 1
    Input = 2
    UserName = 3

class Message:
    def __init__(self, message_type, message):
        self.message_type = message_type
        self.message = message

def parseMessage(message):
    global CONNECTION_OPEN
    rec_message = Message(message['type'], message['message'])
    print(rec_message.message_type)
    print(rec_message.message)
    if rec_message.message_type == MessageType.UserName:
        print("Username")
        USERNAME = rec_message.message
        send_message = json.dumps({'type': MessageType.Input, 'message': '255,255,255,0'})
        return send_message
    elif rec_message.message_type == MessageType.Input:
        print("Received input")
        CONNECTION_OPEN = False
        send_message = json.dumps({'type': MessageType.Close, 'message': 'Closing connection'})
        return send_message
    elif rec_message.message_type == MessageType.Close:
        print("Close connection")
        send_message = json.dumps({'type': MessageType.Close, 'message': 'Closing connection'})
        CONNECTION_OPEN = False
        return send_message

async def sendMessage(ws, message):
    await ws.send(message)
    server_message = json.loads(await ws.recv())
    message = parseMessage(server_message)
    print("Second send", message)

async def init_connection(message):
    print("Initial message:", message)
    global CONNECTION_OPEN
    uri = "ws://192.168.174.97:8081"
    async with websockets.connect(uri) as websocket:
        # send init message
        await websocket.send(message)
        while True:
            server_message = json.loads(await websocket.recv())
            message = parseMessage(server_message)
            await sendMessage(websocket, message)
            print("Message after parse:", message)
        #CONNECTION_OPEN = False
        #print("received message", json.load(message))

while CONNECTION_OPEN:
    message = json.dumps({'type': MessageType.Init, 'message': 'Init'})
    asyncio.get_event_loop().run_until_complete(init_connection(message))
