import unittest
import lights
from message_handler import MessageHandler

class TestLightMethods(unittest.TestCase):

    def test_get_lamp_state(self):
        handler = MessageHandler()
        handler.set_connection(True)
        lights.STATE = "NOT IDLE"
        self.assertEqual("SetLight", lights.get_lamp_state(True, handler))
        lights.STATE = "IDLE"
        self.assertEqual("IDLE", lights.get_lamp_state(True, handler))
        self.assertEqual("NOTIDLE", lights.get_lamp_state(False, handler))
        handler.set_connection(False)
        self.assertEqual("IDLENotConnected", lights.get_lamp_state(True, handler))

    

if __name__ == '__main__':
    unittest.main()

