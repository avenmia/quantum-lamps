import websocket
import asyncio
import json
try:
    import thread
except ImportError:
    import _thread as thread
import time
from enum import IntEnum

USERNAME = ""

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

    rec_message = Message(message['type'], message['message'])
    print(rec_message.message_type)
    print(rec_message.message)
    if rec_message.message_type == MessageType.UserName:
        print("Username")
        USERNAME = rec_message.message
        print("Printing username", USERNAME)
    elif rec_message.message_type == MessageType.Input:
        print("Received input")
    elif rec_message.message_type == MessageType.Close:
        print("Close connection")
    


def on_message(ws, message):
    print(json.loads(message))
    parsedMessage = json.loads(message)
    parseMessage(parsedMessage)

def on_error(ws, error):
    print(error)

def on_close(ws):
    
    print("### closed ###")

def on_open(ws):
    def run(*args):
        ws.send(json.dumps({'type': MessageType.Init, 'message': 'Init'}))
        time.sleep(1)
        ws.close()
        print("thread terminating...")
    thread.start_new_thread(run, ())


if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://localhost:8081",
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()

#ws.connect("ws://localhost.com:8081")