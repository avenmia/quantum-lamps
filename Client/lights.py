import digitalio
import busio
import adafruit_lis3dh
import board
import neopixel
import numpy as np
import asyncio
import RPi.GPIO as GPIO

# LED strip configuration:
LED_COUNT = 16  # Number of LED pixels.
LED_PIN = board.D18  # GPIO pin
LED_BRIGHTNESS = .1  # LED brightness
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

# Create NeoPixel object with appropriate configuration.
strip = neopixel.NeoPixel(LED_PIN, LED_COUNT, brightness=LED_BRIGHTNESS, auto_write=False, pixel_order=LED_ORDER)

i2c = busio.I2C(board.SCL, board.SDA)
int1 = digitalio.DigitalInOut(board.D6)  # Set this to the correct pin for the interrupt!
lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c, int1=int1)
# Create a way to fade/transition between colors using numpy arrays


def accel_to_color(x, y, z):
    return (255/(abs(x)+1), 255/(abs(y) + 1), 255/(abs(z) + 1))


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
            strip.fill((fade(color1, color2, percent)))
            strip.show()
            await asyncio.sleep(wait)


async def do_fade(color1, color2):
    for i in range(10):
        percent = i*0.1   # 0.1*100 so 10% increments between colors
        strip.fill((fade(color1, color2, percent)))
        strip.show()
        await asyncio.sleep(0.1)


def is_lamp_idle(sx, sy, sz):
    return sx < 0.3 or sy < 0.3 or sz < 0.3


async def rainbow_cycle(wait):
    for j in range(255):
        for i in range(LED_COUNT):
            rc_index = (i * 256 // LED_COUNT) + j
            strip[i] = wheel(rc_index & 255)
        strip.show()
        await asyncio.sleep(wait)


async def set_lamp_light(color1, handler):
    global STATE
    strip.fill(color1)
    strip.show()
    # TODO: Keep lamp the same color until not idle
    while STATE != "NOT IDLE":
        print("Waiting for it to not be idle")
        await calculate_idle(3, handler)
    await asyncio.sleep(3)


async def handle_lamp_state(is_idle, handler):
    global STATE
    is_connected = handler.get_connection()
    print("Handler connection in lights:", handler.get_connection())
    if is_idle and STATE == "NOT IDLE" and is_connected:
        STATE = "IDLE"
        curr_color = handler.get_light_data()
        print("Sending color", curr_color)
        await asyncio.sleep(1)
    elif is_idle and is_connected:
        # Check for data
        STATE = "IDLE"
        print("Pretending to send for now")
        curr_color = handler.get_light_data()
        handler.create_message("Input", curr_color)
        message = handler.get_message()
        await handler.send_message(message)
        print("Message sent from idle")
        await asyncio.sleep(1)
    elif is_idle and not is_connected:
        print("Idle and not connected")
        await rainbow_cycle(0.001)    # rainbow cycle with 1ms delay per step
        await asyncio.sleep(1)
    else:
        STATE = "NOT IDLE"
        await asyncio.sleep(1)
        print("Is not idle")


async def change_current_light(t, handler):
    global prevColor
    x_arr = []
    y_arr = []
    z_arr = []
    while t >= 0:
        x, y, z = lis3dh.acceleration
        print("Current colors")
        print(accel_to_color(x, y, z))
        x_arr.append(x)
        y_arr.append(y)
        z_arr.append(z)
        newColor = accel_to_color(x, y, z)
        # remember prev color
        await do_fade(prevColor, newColor)
        prevColor = newColor
        handler.set_light_data(newColor)
        await asyncio.sleep(.2)
        t -= .2
    return [x_arr, y_arr, z_arr]


async def calculate_idle(t, handler):
    orig_time = t
    while True:
        [x_arr, y_arr, z_arr] = await change_current_light(orig_time, handler)
        is_idle = is_lamp_idle(np.std(x_arr), np.std(y_arr), np.std(z_arr))
        await handle_lamp_state(is_idle, handler)
