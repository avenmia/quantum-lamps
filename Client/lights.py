import digitalio
import busio
import adafruit_lis3dh
import board
import neopixel
import numpy as np
import asyncio
import math
import logging
from lamp_states import LampState
import RPi.GPIO as GPIO

# LED strip configuration:
LED_COUNT = 16  # Number of LED pixels.
LED_PIN = board.D18  # GPIO pin
LED_BRIGHTNESS = 0.2  # LED brightness
LED_ORDER = neopixel.RGBW  # order of LED colors. May also be RGB, GRBW, or RGBW

USERNAME = ""
STATE = "IDLE"
INCOMING_DATA = False
prevColor = (0, 0, 0)
# BUTTON_PIN = board.D25 # python button input

GPIO.setwarnings(False)
GPIO.setup(15, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# The color selection selected for this project: red, blue, yellow, green, pink, and silver respectively

gokai_colors = [(255, 0, 0), (0, 0, 255), (255, 255, 0), (0, 255, 0), (255, 105, 180), (192, 192, 192)]
red_colors = [(0, 250, 0), (0, 200, 0), (0, 150, 0), (0, 100, 0), (0, 50, 0)]

# Create NeoPixel object with appropriate configuration.
strip = neopixel.NeoPixel(LED_PIN, LED_COUNT, brightness=LED_BRIGHTNESS, auto_write=False, pixel_order=LED_ORDER)

i2c = busio.I2C(board.SCL, board.SDA)
int1 = digitalio.DigitalInOut(board.D6)  # Set this to the correct pin for the interrupt!
lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c, int1=int1)
# Create a way to fade/transition between colors using numpy arrays

lock = asyncio.Lock()
loop = asyncio.new_event_loop()
event = asyncio.Event(loop=loop)


def accel_to_color(x, y, z):
    return (math.ceil(255/(abs(x)+1)), math.ceil(255/(abs(y) + 1)), math.ceil(255/(abs(z) + 1)))


def fade(color1, color2, percent):
    color1 = np.array(color1)
    color2 = np.array(color2)
    vector = color2-color1
    newcolor = (int((color1 + vector * percent)[0]), int((color1 + vector * percent)[1]), int((color1 + vector * percent)[2]))
    return newcolor


# Main function loop
def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colors are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos*3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos*3)
        g = 0
        b = int(pos*3)
    else:
        pos -= 170
        r = 0
        g = int(pos*3)
        b = int(255 - pos*3)
    return (r, g, b) if LED_ORDER == neopixel.RGB or LED_ORDER == neopixel.GRB else (r, g, b, 0)


async def rollcall_cycle(wait):
    for j in range(len(gokai_colors)):
        for i in range(10):
            color1 = gokai_colors[j]
            if j == 5:
                color2 = (255, 255, 255)
            else:
                color2 = gokai_colors[(j+1)]
            percent = i*0.1   # 0.1*100 so 10% increments between colors
            logging.debug("Setting light in rollcall")
            strip.fill((fade(color1, color2, percent)))
            strip.show()
            await asyncio.sleep(wait)


async def rollcall_cycle_scheme(wait, color_scheme):
    for j in range(len(color_scheme)):
        for i in range(10):
            color1 = color_scheme[j]
            if j == 5:
                color2 = (255, 255, 255)
            else:
                color2 = color_scheme[(j+1)]
            percent = i*0.1   # 0.1*100 so 10% increments between colors
            logging.debug("Setting light in rollcall")
            strip.fill((fade(color1, color2, percent)))
            strip.show()
            await asyncio.sleep(wait)


async def dim_down(wait, color_scheme):
    logging.debug(f'starting brightness {strip.brightness}')
    for color in color_scheme:
        for i in range(2, 0, -1):
            strip.fill(color)
            strip.brightness = i / 2.0
            strip.show()
            logging.debug(f'Fading from {strip.brightness}')
            await asyncio.sleep(wait)
        strip.brightness = LED_BRIGHTNESS
        strip.fill(color)
        strip.show()


async def blink(wait, color):
    strip.fill(color)
    strip.brightness = LED_BRIGHTNESS / 2.0
    strip.show()
    await asyncio.sleep(wait)
    strip.brightness = LED_BRIGHTNESS
    strip.fill(color)
    strip.show()
    await asyncio.sleep(wait)


async def do_fade(color1, color2, handler):
    logging.debug(f'fading from {color1} to {color2}')
    for i in range(10):
        percent = i*0.1   # 0.1*100 so 10% increments between colors
        strip.fill((fade(color1, color2, percent)))
        strip.show()
        await asyncio.sleep(0.1)


def is_lamp_idle(sx, sy, sz):
    return sx < 0.5 or sy < 0.5 or sz < 0.5


async def rainbow_cycle(wait):
    for j in range(255):
        for i in range(LED_COUNT):
            rc_index = (i * 256 // LED_COUNT) + j
            strip[i] = wheel(rc_index & 255)
        strip.show()
        await asyncio.sleep(wait)


async def change_current_light(t, change_color, handler):
    global prevColor
    x_arr = []
    y_arr = []
    z_arr = []
    while t >= 0:
        x, y, z = lis3dh.acceleration
        x_arr.append(x)
        y_arr.append(y)
        z_arr.append(z)
        newColor = accel_to_color(x, y, z)
        if change_color:
            await event.wait()
            # remember prev color
            logging.debug("Changing color")
            await do_fade(prevColor, newColor, handler)
            handler.set_light_data(newColor)
            logging.debug("Changed color")
            prevColor = newColor
        await asyncio.sleep(.05)
        t -= .05
    return [x_arr, y_arr, z_arr]


# Function to keep light the same color
# until interrupted by message
# or by moving the lamp
async def keep_light(handler, data):
    if handler.get_light_data() != data:
        handler.set_light_data(data)
    logging.debug(f'Setting light in keep light to: {handler.get_light_data()}')
    set_light(handler)
    while True:
        is_idle = await calculate_idle(1, handler, False)
        set_light(handler)
        new_message = handler.get_new_message()
        # If not idle or incoming message
        logging.debug(f'Is Idle: {is_idle}')
        logging.debug(f'New Message {new_message}')
        logging.debug(f'Current light in keep light to: {handler.get_light_data()}')
        if not is_idle or new_message:
            logging.debug("Breaking freeeeee")
            break
    await asyncio.sleep(1)
    return "Finished"


def set_light(handler):
    strip.fill(handler.get_light_data())
    strip.show()


async def monitor_idle(handler, data):
    is_idle = True
    if handler.get_light_data() != data:
        logging.debug(f'Setting light data back: {data}')
        handler.set_light_data(data)
    while is_idle:
        is_idle = await calculate_idle(1, handler, False)
        logging.debug(f'Is idle: {is_idle}')
        handler.set_light_data(data)
        set_light(handler)
    event.set()


async def blink_red():
    [x, y, z] = accel_to_color(255, 0, 255)
    await blink(.5, [int(x), int(y), int(z)])
    await blink(.5, [int(x), int(y), int(z)])
    await blink(.5, [int(x), int(y), int(z)])

async def blink_green():
    [x, y, z] = accel_to_color(0, 255, 255)
    await blink(.5, [int(x), int(y), int(z)])
    await blink(.5, [int(x), int(y), int(z)])
    await blink(.5, [int(x), int(y), int(z)])


async def maintain_light(handler, data):
    logging.debug(f'Maintain light data: {data}')
    mon_idle = loop.create_task(monitor_idle(handler, data))
    mon_idle.set_name("monitor_idle")
    loop.call_soon_threadsafe(asyncio.ensure_future, mon_idle)


async def handle_current_lamp_state(lamp_state, input_message, handler):
    if lamp_state == LampState.SETLIGHT:
        # If the request did not come from the server
        # Send data to server
        if not input_message:
            # Send Message
            event.clear()
            logging.info("Handling user set light")
            curr_color = handler.get_light_data()
            if handler.get_connection():
                handler.create_message("Input", curr_color)
                message = handler.get_message()
                logging.debug(f'Message is: {message}')
                await blink_red()
                await handler.send_message(message)
            else:
                await blink_green()

            logging.debug(f'Current color is: {curr_color}')
    
            async with lock:
                mon_task = [x for x in asyncio.all_tasks() if x.get_name() == "monitor_idle"]
                if len(mon_task) > 0:
                    logging.debug("Canceling previous mon task")
                    mon_task[0].cancel()
                await maintain_light(handler, curr_color)
            logging.debug("Releasing lock in current lamp")
        else:
            logging.info("Handling input message")
    elif lamp_state == LampState.IDLE:
        logging.info("Lamp is idle and connected")
    elif lamp_state == LampState.IDLENOTCONNECT:
        logging.info("Lamp is idle and not connected")
    else:
        event.set()
        logging.info("Lamp is not Idle")


def get_lamp_state(is_idle, handler):
    global STATE
    is_connected = handler.get_connection()
    if is_idle and STATE == "NOT IDLE" and is_connected:
        STATE = "IDLE"
        # Change to ENUM
        return LampState.SETLIGHT
    elif is_idle and is_connected:
        # Check for data
        STATE = "IDLE"
        return LampState.IDLE
    elif is_idle and STATE == "NOT IDLE" and not is_connected:
        STATE = "IDLE"
        return LampState.SETLIGHT
    else:
        STATE = "NOT IDLE"
        return LampState.NOTIDLE


# This only gets called from the "main" thread
async def read_light_data(handler):
    while True:
        # Get lamp data
        is_idle = await calculate_idle(.1, handler, True)
        logging.debug(f'Is Idle: {is_idle}')
        lamp_state = get_lamp_state(is_idle, handler)
        await handle_current_lamp_state(lamp_state, False, handler)
    logging.debug("Exiting read light data")


# This is called from main or from keep light
# Returns true or false whether the lamp is idle
async def calculate_idle(t, handler, change_color):
    orig_time = t
    [x_arr, y_arr, z_arr] = await change_current_light(orig_time, change_color, handler)
    return is_lamp_idle(np.std(x_arr), np.std(y_arr), np.std(z_arr))
