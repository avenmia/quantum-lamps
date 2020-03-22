#!/usr/bin/env python

import os
import asyncio
import websockets
import json
import threading
import time
from random import randrange
from enum import Enum
from lights import calculate_idle #, client_connect_var, ctx, contextvars

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
    #global CONNECTION_OPEN
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
    global CONNECTION_OPEN
    global CLIENT_WS
    uri = WS_URI
    async with websockets.connect(uri) as websocket:
        print("Setting Connection open to true")
        CONNECTION_OPEN = True
        # client_connect_var.set(True)
        # print("Printing ctx after set")
        # print("Does client connect exist?", client_connect_var in ctx)
        # print("Current client connect value:", ctx[client_connect_var])
        # print("Value from the getter:", client_connect_var.get())
        # print("Where tf is this", client_connect_var)
        # print("CTX in init_connection:", ctx)
        CLIENT_WS = websocket
        # send init message
        print("Sending message")
        await websocket.send(message)
        print("Connection is open")
        print("Printing init_connection address", hex(id(CONNECTION_OPEN))) 
        while CONNECTION_OPEN:
            await handleMessages(websocket, message)
            # if GPIO.input(15) == GPIO.LOW:
            #         print("Button was pushed")
        await websocket.send(json.dumps({'type': MessageType.Close.name, 'message': USERNAME}))
        await websocket.close()
##########################################################

## Collect background data ##
count = 0
current_data = 0

async def run():
    print("Starting background task")
    global current_data
    global count
    while True:
        print("Count is:", count)
        count = count + 1
        if count % 6 == 0:
            current_data = count + randrange(25)
            message = json.dumps(
        {'type': MessageType.Input.name, 'payload': current_data})
            if CLIENT_WS is not None:
                print("Sending message to server after not idle")
                await sendMessage(CLIENT_WS, message, False)
        
        await asyncio.sleep(1)   

def get_current_data():
    global current_data
    return current_data

def set_current_data(val):
    global current_data
    if current_data != val:
        current_data = val
    print("Setting current data to", current_data)


##########################################################
print("Starting background process")

async def main():
    message = json.dumps({'type': "Auth", 'payload': {
                            'username': 'Mike', 'secret': SHARED_SECRET}})
    loop = asyncio.get_event_loop()
    start_light = asyncio.create_task(calculate_idle(3))
    await asyncio.gather(init_connection(message), start_light)

#ctx.run(asyncio.run(main()))
asyncio.run(main())