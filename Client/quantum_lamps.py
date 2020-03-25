#!/usr/bin/env python

import os
import asyncio
import websockets
import json
from message_handler import MessageHandler
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
        send_message = await HandleInput(rec_message.payload)
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


async def HandleInput(payload):
    data = clean_incoming_data(payload)
    await lights.set_lamp_light(data)
    return json.dumps(
        {'type': MessageType.Listening.name, 'payload': 'Listening'})


def clean_incoming_data(payload):
    return tuple(payload)


def HandleClosing():
    global USERNAME
    print("Closing connection")
    return json.dumps(
        {'type': MessageType.Close.name, 'payload': USERNAME})


def HandleClose():
    # Shouldn't get hit
    print("Close connection")


async def sendMessage(ws, message, recieve):
    await ws.send(message)
    if recieve:
        server_message = json.loads(await ws.recv())
        message = await parseMessage(ws, server_message)


async def handleMessages(ws, message, handler):
    try:
        async for message in ws:
            print(message)
            server_message = json.loads(message)
            await parseMessage(ws, server_message)
    except websockets.exceptions.ConnectionClosed:
        pass


async def init_connection(message, handler):
    print("Initial message:", message)
    global CLIENT_WS
    uri = WS_URI
    async with websockets.connect(uri) as websocket:
        print("Setting Connection open to true")

        handler.set_connection(True)
        handler.set_websocket(websocket)
        is_connected = handler.get_connection()
        print("handler connection:", is_connected)
        CLIENT_WS = websocket
        # send init message
        print("Sending message")
        await websocket.send(message)
        print("Connection is open")
        while is_connected:
            await handleMessages(websocket, message, handler)
            # if GPIO.input(15) == GPIO.LOW:
            #         print("Button was pushed")
        await websocket.send(json.dumps({'type': MessageType.Close.name, 'message': USERNAME}))
        await websocket.close()
##########################################################


async def main():
    handler = MessageHandler()
    message = json.dumps({'type': "Auth", 'payload': {
        'username': 'Mike', 'secret': SHARED_SECRET}})
    start_light = asyncio.create_task(lights.calculate_idle(3, handler))
    await asyncio.gather(init_connection(message, handler), start_light)

asyncio.run(main())
