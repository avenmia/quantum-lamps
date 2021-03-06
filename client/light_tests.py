import unittest
import lights
import asyncio
from message_handler import MessageHandler


def async_test(coro):
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        return loop.run_until_complete(coro(*args, **kwargs))
    return wrapper


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

    def test_set_light(self):
        handler = MessageHandler()
        [x, y, z] = lights.accel_to_color(0, 0, 255)
        handler.set_light_data([int(x), int(y), int(z)])
        lights.set_light(handler)
        self.assertEqual([255, 255, 0], handler.get_light_data())

    @async_test
    async def test_keep_light(self):
        handler = MessageHandler()
        [x, y, z] = lights.accel_to_color(0, 0, 255)
        handler.set_light_data([int(x), int(y), int(z)])
        print("Original light:", handler.get_light_data())
        handler.set_new_message(True)
        result = await lights.keep_light(handler)
        self.assertEqual("Finished", result)
        self.assertEqual([255, 255, 0], handler.get_light_data())

    @async_test
    async def test_blink(self):
        [x, y, z] = lights.accel_to_color(255, 0, 255)
        await lights.blink(.5, [int(x), int(y), int(z)])
        await lights.blink(.5, [int(x), int(y), int(z)])
        await lights.blink(.5, [int(x), int(y), int(z)])
        print(f'Ending brightness: {lights.strip.brightness}')

    @async_test
    async def test_rainbow_cycle(self):
        await lights.rainbow_cycle(.001)

    def test_accel_to_color(self):
        self.assertEqual(lights.accel_to_color(0, 0, 0), (255, 255, 255))
        self.assertEqual(lights.accel_to_color(255, 255, 255), (1, 1, 1))


if __name__ == '__main__':
    unittest.main()
