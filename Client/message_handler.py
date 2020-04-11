import json


class MessageHandler:

    def __init__(self):
        self.message = None
        self.current_state = None
        self.light_data = None
        self.websocket = None
        self.is_connected = False
        self.new_message = False

    def get_websocket(self):
        return self.websocket

    def set_websocket(self, ws):
        self.websocket = ws

    def get_connection(self):
        return self.is_connected

    def set_connection(self, is_connected):
        self.is_connected = is_connected

    def set_message(self, message):
        self.message = message

    def get_message(self):
        return self.message

    def set_current_state(self, state):
        self.current_state = state

    def get_current_state(self):
        return self.current_state

    def set_light_data(self, data):
        print("Data is :", data)
        self.light_data = data

    def get_light_data(self):
        return self.light_data

    def get_new_message(self):
        return self.new_message

    def set_new_message(self, data):
        print("Setting message to:", data)
        self.new_message = data

    def create_message(self, message_type, message_data):
        message = json.dumps({'type': message_type, 'payload': message_data})
        self.set_message(message)

    async def send_message(self, message):
        await self.websocket.send(message)
