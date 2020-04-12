#!/usr/bin/env python

import os
import sys
import asyncio
import websockets
import json
from message_handler import MessageHandler
from enum import Enum
import lights
import traceback

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
    print(rec_message.message_type)
    print(rec_message.payload)
    if rec_message.message_type == MessageType.Username.name:
        send_message = HandleUsername(rec_message.payload)
    elif rec_message.message_type == MessageType.Input.name:
        await HandleInput(rec_message.payload, handler)
        print("Returning from parse message")
        return
    elif rec_message.message_type == MessageType.Closing.name:
        send_message = HandleClosing()
    elif rec_message.message_type == MessageType.Close.name:
        HandleClose()
    await sendMessage(ws, send_message, True, handler)


def HandleUsername(payload):
    global USERNAME
    print("Username")
    USERNAME = payload
    return json.dumps(
        {'type': MessageType.Listening.name, 'payload': 'Listening'})


async def HandleInput(payload, handler):
    lock = lights.lock
    lights.event.set()
    async with lock:
        print("In locked state")
        data = clean_incoming_data(payload)
        print("Here is incoming light data", data)
        print("Clearing the lock")
        lights.event.clear()
        handler.set_light_data(data)
        print(f'Before tasks handler is: {handler.get_light_data()}')
        print(f'Before incoming data is: {data}')
        for task in asyncio.all_tasks():
            if task.get_name() == "maintain_light":
                task.cancel()

        #This approach creates a new task and returns to the websocket executor?
        # 1 Doesn't work returns to the websocket task and gets blocked waiting for incoming signal
        # maintain_light = lights.loop.create_task(lights.input_light(handler, data))
        # maintain_light.set_name("maintain_light")
        
        # 2
        # maintain_light = lights.loop.create_task(lights.input_light(handler, data))
        try:
            # 1 Doesn't work returns to the websocket task and gets blocked waiting for incoming signal
            #lights.loop.call_soon_threadsafe(asyncio.ensure_future, maintain_light)
            
            # 2
            #lights.loop.run_until_complete(maintain_light)
           
            # 1 
            # Doesn't work. lights.input_light doesn't block the event loop
            #result = await lights.loop.run_in_executor(None, lights.input_light(handler, data))
            print(f'Result: {result} out of here')
        except TypeError as err:
            traceback.print_exc()
            print(f'TypeError is: {err}')
        except:
            traceback.print_exc()
            print(f'Error is:',sys.exc_info()[0])
        # 3
        await lights.input_light(handler, data)
        
    print("Releasing lock")
    return json.dumps(
        {'type': MessageType.Listening.name, 'payload': 'Listening'})


def clean_incoming_data(payload):
    print("Cleaning data:", tuple(payload))
    [x,y,z] = tuple(payload)
    print("x, y, z", [x,y,z])
    return [int(x), int(y), int(z)]


def HandleClosing():
    global USERNAME
    print("Closing connection")
    return json.dumps(
        {'type': MessageType.Close.name, 'payload': USERNAME})


def HandleClose():
    # Shouldn't get hit
    print("Close connection")


async def sendMessage(ws, message, recieve, handler):
    await ws.send(message)
    if recieve:
        print("Message received")
        server_message = json.loads(await ws.recv())
        message = await parseMessage(ws, server_message, handler)


async def handleMessages(ws, message, handler):
    print("Handling directly")
    try:
        async for message in ws:
            print(message)
            print("handling that message")
            server_message = json.loads(message)
            await parseMessage(ws, server_message, handler)
    except websockets.exceptions.ConnectionClosed:
        pass


async def init_connection(message, handler):
    print("Initial message:", message)
    global CLIENT_WS
    uri = WS_URI
    print("URI is:", uri)
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
            print("Still connected")
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
    start_light = asyncio.create_task(lights.read_light_data(handler))
    start_light.set_name("start light")
    print("Clearing event")
    
    # Event set clears lock
    lights.event.set()
    print("Event cleared")
    await asyncio.gather(init_connection(message, handler), start_light)


# asyncio.run(main())
lights.loop.run_until_complete(main())
