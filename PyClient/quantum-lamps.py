#!/usr/bin/env python

import os
import asyncio
import websockets
import json
from sampledata import get_current_data, set_current_data
from enum import Enum


# WebSocket Code #
class MessageType(Enum):
    Close = 1
    Closing = 2
    Auth = 3
    Input = 4
    Listening = 5
    Username = 6


class Message:
    def __init__(self, message_type, payload):
        self.message_type = message_type
        self.payload = payload


async def parseMessage(ws, message):
    global CONNECTION_OPEN
    global USERNAME
    send_message = ""
    rec_message = Message(message['type'], message['payload'])
    print(rec_message.message_type)
    print(rec_message.payload)
    if rec_message.message_type == MessageType.Username.name:
        print("Username")
        USERNAME = rec_message.payload
        data = get_current_data()
        send_message = json.dumps(
            {'type': MessageType.Input.name, 'payload': data})
    elif rec_message.message_type == MessageType.Input.name:
        print("Received input")
        #CONNECTION_OPEN = False
        data = get_current_data()
        incoming_data = int(rec_message.payload)
        if incoming_data != data:
            set_current_data(incoming_data)
        print("Incoming data is", incoming_data)
        print("Data is:", data)
        send_message = json.dumps(
            {'type': MessageType.Input.name, 'payload': data})
        CONNECTION_OPEN = False
    elif rec_message.message_type == MessageType.Closing.name:
        print("Close connection")
        send_message = json.dumps(
            {'type': MessageType.Close.name, 'payload': USERNAME})
        CONNECTION_OPEN = False
    elif rec_message.message_type == MessageType.Close.name:
        # Shouldn't get hit
        CONNECTION_OPEN = False
    await ws.send(send_message)


async def sendMessage(ws, message):
    await ws.send(message)
    server_message = json.loads(await ws.recv())
    message = parseMessage(ws, server_message)

async def handleMessages(ws, message):
    loop = asyncio.get_event_loop()
    try:
        async for message in ws:
            print(message)
            server_message = json.loads(message)
            loop.create_task(parseMessage(ws,server_message))
    except websockets.exceptions.ConnectionClosed:
        pass

async def init_connection(message):
    # calculate_idle(3)
    print("Initial message:", message)
    global CONNECTION_OPEN
    uri = "ws://localhost:8081"
    async with websockets.connect(uri) as websocket:
        CONNECTION_OPEN = True
        # send init message
        await websocket.send(message)
        while CONNECTION_OPEN:
            await handleMessages(websocket, message)
            # if GPIO.input(15) == GPIO.LOW:
            #         print("Button was pushed")
            # server_message = json.loads(await websocket.recv())
            #print("Server message:", server_message)
            #message = parseMessage(server_message)
            #await sendMessage(websocket, message)
            #print("Message after parse:", message)
        await websocket.send(json.dumps({'type': MessageType.Close.name, 'message': USERNAME}))
        await websocket.close()
        #CONNECTION_OPEN = False
        #print("received message", json.load(message))
##########################################################

while True:
    SHARED_SECRET = os.environ['SHARED_SECRET']
    print("Shared secret", SHARED_SECRET)
    message = json.dumps({'type': "Auth", 'payload': {
                         'username': 'Mike', 'secret': SHARED_SECRET}})
    asyncio.get_event_loop().run_until_complete(init_connection(message))
