#!/usr/bin/env python

import os
import asyncio
import websockets
import json
import threading
import time
from random import randrange
from enum import Enum
import lights

from dotenv import load_dotenv
load_dotenv()
SHARED_SECRET = os.environ['SHARED_SECRET']
WS_URI = os.environ['WS_URI']


CLIENT_WS = None

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
    send_message = ""
    rec_message = Message(message['type'], message['payload'])
    print(rec_message.message_type)
    print(rec_message.payload)
    if rec_message.message_type == MessageType.Username.name:
        send_message = HandleUsername(rec_message.payload)
    elif rec_message.message_type == MessageType.Input.name:
        send_message = HandleInput(rec_message.payload)
    elif rec_message.message_type == MessageType.Closing.name:
        send_message = HandleClosing()
    elif rec_message.message_type == MessageType.Close.name:
        HandleClose()
    await sendMessage(ws, send_message, True)

def HandleUsername(payload):
    global USERNAME
    print("Username")
    USERNAME = payload
    return json.dumps(
            {'type': MessageType.Listening.name, 'payload': 'Listening'})

def HandleInput(payload):
    print("Received input")
    data = get_current_data()
    incoming_data = int(payload)
    if incoming_data != data:
        set_current_data(incoming_data)
    print("Incoming data is", incoming_data)
    print("Data is:", data)
    return json.dumps(
            {'type': MessageType.Listening.name, 'payload': 'Listening'})

def HandleClosing():
    global USERNAME
    #global CONNECTION_OPEN
    #CONNECTION_OPEN = False
    print("Closing connection")
    return json.dumps(
        {'type': MessageType.Close.name, 'payload': USERNAME})

def HandleClose():
    #global CONNECTION_OPEN
    # Shouldn't get hit
    print("Close connection")
    #CONNECTION_OPEN = False

async def sendMessage(ws, message, recieve):
    await ws.send(message)
    if recieve == True:
        server_message = json.loads(await ws.recv())
        message = await parseMessage(ws, server_message)

async def handleMessages(ws, message):
    try:
        async for message in ws:
            print(message)
            server_message = json.loads(message)
            await parseMessage(ws, server_message)
            #loop.create_task(parseMessage(ws,server_message))
    except websockets.exceptions.ConnectionClosed:
        pass

async def init_connection(message):
    print("Initial message:", message)
    global CLIENT_WS
    uri = WS_URI
    async with websockets.connect(uri) as websocket:
        print("Setting Connection open to true")
        lights.CONNECTION_OPEN = True
        CLIENT_WS = websocket
        # send init message
        print("Sending message")
        await websocket.send(message)
        print("Connection is open")
        print("Printing init_connection address", hex(id(lights.CONNECTION_OPEN))) 
        while lights.CONNECTION_OPEN:
            await handleMessages(websocket, message)
            # if GPIO.input(15) == GPIO.LOW:
            #         print("Button was pushed")
        await websocket.send(json.dumps({'type': MessageType.Close.name, 'message': USERNAME}))
        await websocket.close()
##########################################################

async def main():
    message = json.dumps({'type': "Auth", 'payload': {
                            'username': 'Mike', 'secret': SHARED_SECRET}})
    loop = asyncio.get_event_loop()
    start_light = asyncio.create_task(lights.calculate_idle(3))
    await asyncio.gather(init_connection(message), start_light)

asyncio.run(main())