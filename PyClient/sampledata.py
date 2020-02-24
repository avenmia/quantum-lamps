import time
import threading
import signal
import json
from quantum_lamps import sendMessage, CLIENT_WS,MessageType
from random import randrange

count = 0
current_data = 0

class CountThread(object):
    def __init__(self, interval=1):
        self.interval = interval
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()
    
    def run(self):
        print("Starting background task")
        global current_data
        global count
        while True:
            print("Count is:", count)
            count = count + 1
            if count % 7 == 0:
                current_data = count + randrange(25)
                message = json.dumps(
            {'type': MessageType.Input.name, 'payload': current_data})
                if CLIENT_WS is not None:
                    sendMessage(CLIENT_WS, message)
            time.sleep(self.interval)

def get_current_data():
    global current_data
    return current_data

def set_current_data(val):
    global current_data
    if current_data != val:
        current_data = val
    print("Setting current data to", current_data)

print("Starting background process")
ct = CountThread()

