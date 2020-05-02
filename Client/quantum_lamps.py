#!/usr/bin/env python

import os
import asyncio
import websockets
import json
from message_handler import MessageHandler
from enum import Enum
import lights
import logging

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


async def parseMessage(ws, message, handler):
    send_message = ""
    rec_message = Message(message['type'], message['payload'])
    if rec_message.message_type == MessageType.Username.name:
        send_message = HandleUsername(rec_message.payload)
    elif rec_message.message_type == MessageType.Input.name:
        await HandleInput(rec_message.payload, handler)
        return
    elif rec_message.message_type == MessageType.Closing.name:
        send_message = HandleClosing()
    elif rec_message.message_type == MessageType.Close.name:
        HandleClose()
    await sendMessage(ws, send_message, True, handler)


def HandleUsername(payload):
    global USERNAME
    logging.debug("Username")
    USERNAME = payload
    return json.dumps(
        {'type': MessageType.Listening.name, 'payload': 'Listening'})


async def HandleInput(payload, handler):
    lock = lights.lock
    logging.debug("Clearing event")
    lights.event.clear()
    async with lock:
        await lights.rainbow_cycle(.001)
        data = clean_incoming_data(payload)
        mon_task = [x for x in asyncio.all_tasks() if x.get_name() == "monitor_idle"]
        if len(mon_task) > 0:
            mon_task[0].cancel()
        await lights.maintain_light(handler, data)
    return json.dumps(
        {'type': MessageType.Listening.name, 'payload': 'Listening'})


def clean_incoming_data(payload):
    [x, y, z] = tuple(payload)
    return [int(x), int(y), int(z)]


def HandleClosing():
    global USERNAME
    logging.info("Closing connection")
    return json.dumps(
        {'type': MessageType.Close.name, 'payload': USERNAME})


def HandleClose():
    # Shouldn't get hit
    logging.info("Close connection")


async def sendMessage(ws, message, recieve, handler):
    await ws.send(message)
    if recieve:
        server_message = json.loads(await ws.recv())
        message = await parseMessage(ws, server_message, handler)


async def handleMessages(ws, message, handler):
    try:
        async for message in ws:
            server_message = json.loads(message)
            await parseMessage(ws, server_message, handler)
    except websockets.exceptions.ConnectionClosed:
        pass


async def init_connection(message, handler):
    global CLIENT_WS
    uri = WS_URI
    try:
        logging.info("Connecting to server")
        async with websockets.connect(uri) as websocket:
            handler.set_connection(True)
            handler.set_websocket(websocket)
            CLIENT_WS = websocket
            await websocket.send(message)
            logging.info("Connection is open")
            await handleMessages(websocket, message, handler)
            logging.info("Connection is closed")
            await websocket.close()
    except TimeoutError as err:
        logging.error(f'Could not connect to web server {err}')
##########################################################


def get_connection_retry_time(t):
    if t == 16:
        return 16
    else:
        return t * 2


async def ensure_connection(handler):
    message = json.dumps({'type': "Auth", 'payload': {
        'username': 'Mike', 'secret': SHARED_SECRET}})
    t = 1
    while True:
        logging.info("Establishing connection")
        await init_connection(message, handler)
        logging.info("Connection closed")
        handler.set_connection(False)
        await asyncio.sleep(t)
        t = get_connection_retry_time(t)
        logging.info(f'Retrying connection in {t} seconds')


async def main():
    handler = MessageHandler()
    start_light = asyncio.create_task(lights.read_light_data(handler))
    start_light.set_name("start light")

    connect = asyncio.create_task(ensure_connection(handler))
    connect.set_name("ws connect")

    lights.event.set()

    something = await connect
    print(f'Something is: {something}')

    await asyncio.gather(connect, start_light)


lights.loop.set_debug(True)
logging.basicConfig(level=logging.INFO)
lights.loop.run_until_complete(main())
