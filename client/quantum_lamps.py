#!/usr/bin/env python

import os
import asyncio
import websockets
import json
from message_handler import MessageHandler
from enum import Enum
import lights
import logging
from typing import Tuple, Any

from dotenv import load_dotenv
load_dotenv()

# Environment Variables
SHARED_SECRET = os.environ['SHARED_SECRET']
WS_URI = os.environ['WS_URI']
USER_NAME = os.environ['USER_NAME']
VERSION = os.environ['VERSION']

class MessageType(Enum):
    Close = 1
    Closing = 2
    Auth = 3
    Input = 4
    Listening = 5
    Username = 6


class Message:
    def __init__(self, message_type: MessageType, payload: Any):
        self.message_type = message_type
        self.payload = payload


async def parse_message(ws, message: Message, handler: MessageHandler) -> None:
    message_to_send = ""
    rec_message = Message(message['type'], message['payload'])
    if rec_message.message_type == MessageType.Username.name:
        message_to_send = handle_username(rec_message.payload)
    elif rec_message.message_type == MessageType.Input.name:
        await handle_input(rec_message.payload, handler)
        return
    elif rec_message.message_type == MessageType.Closing.name:
        message_to_send = handle_closing()
    elif rec_message.message_type == MessageType.Close.name:
        handle_close()
    await send_message(ws, message_to_send, True, handler)


def handle_username(payload: str):
    global USERNAME
    logging.debug("Username")
    USERNAME = payload
    return json.dumps(
        {'type': MessageType.Listening.name, 'payload': 'Listening'})


async def handle_input(payload: Tuple[str, str, str], handler: MessageHandler):
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


def clean_incoming_data(payload: Tuple[str, str, str]):
    [x, y, z] = tuple(payload)
    return [int(x), int(y), int(z)]


def handle_closing():
    global USERNAME
    logging.info("Closing connection")
    return json.dumps(
        {'type': MessageType.Close.name, 'payload': USERNAME})


def handle_close() -> None:
    # Shouldn't get hit
    logging.info("Close connection")


async def send_message(ws, message: str, receive: bool, handler: MessageHandler) -> None:
    await ws.send(message)
    if receive:
        server_message = json.loads(await ws.recv())
        message = await parse_message(ws, server_message, handler)


async def handle_messages(ws, message: str, handler: MessageHandler) -> None:
    try:
        async for message in ws:
            server_message = json.loads(message)
            await parse_message(ws, server_message, handler)
    except websockets.exceptions.ConnectionClosed:
        pass


async def init_connection(message: str, handler: MessageHandler) -> None:
    """Initiate websocket connection and bind message handler

    Args:
        message (str): Auth Message
        handler (MessageHandler): Message handler
    """
    uri = WS_URI
    try:
        logging.info("Connecting to server")
        async with websockets.connect(uri) as websocket:
            handler.set_connection(True)
            handler.set_websocket(websocket)
            await websocket.send(message)
            logging.info("Connection is open")
            await handle_messages(websocket, message, handler)
            logging.info("Connection is closed")
            await websocket.close()
    except TimeoutError as err:
        logging.error(f'Could not connect to web server {err}')


def get_connection_retry_time(time: int) -> int:
    """Returns time to wait for connection retry

    Args:
        time (int): current retry wait time

    Returns:
        int: next retry wait time
    """
    return time if (time == 16) else time * 2


async def ensure_connection(handler: MessageHandler) -> None:
    """Task that attempts server connection, if connection closes, it waits for retry period.

    Args:
        handler (MessageHandler): Message handler
    """
    message = json.dumps({'type': "Auth", 'payload': {
        'username': USER_NAME, 'secret': SHARED_SECRET}})
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
    """Start asyncio tasks
    """
    handler = MessageHandler()

    logging.debug("Starting light task")
    start_light = asyncio.create_task(lights.read_light_data(handler))
    start_light.set_name("start light")

    connect = asyncio.create_task(ensure_connection(handler))
    connect.set_name("ws connect")

    lights.event.set()

    await asyncio.gather(connect, start_light)


if __name__ == '__main__':
    logging.info(f"Starting quantum lamps client")
    logging.info(f"Version {VERSION}")
    """Bootstrap app
    """
    lights.loop.set_debug(True)
    logging.basicConfig(level=logging.INFO)
    lights.loop.run_until_complete(main())
