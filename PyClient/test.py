#!/usr/bin/env python

import time
import digitalio
import busio
import adafruit_lis3dh
import os
import board
import neopixel
import numpy as np
import asyncio
import websockets
import json
from enum import IntEnum


# LED strip configuration:
LED_COUNT   = 16      # Number of LED pixels.
LED_PIN     = board.D18      # GPIO pin
LED_BRIGHTNESS = 1.0  # LED brightness
LED_ORDER = neopixel.RGBW # order of LED colors. May also be RGB, GRBW, or RGBW
CONNECTED = False
STATE = "IDLE"
INCOMING_DATA = False
prevColor = (0,0,0)

# The color selection selected for this project: red, blue, yellow, green, pink, and silver respectively

gokai_colors = [(255,0,0),(0,0,255),(255,255,0),(0,255,0),(255,105,180),(192,192,192)]

# Create NeoPixel object with appropriate configuration.
strip = neopixel.NeoPixel(LED_PIN, LED_COUNT, brightness = LED_BRIGHTNESS, auto_write=False, pixel_order = LED_ORDER)

i2c = busio.I2C(board.SCL, board.SDA)
int1 = digitalio.DigitalInOut(board.D6)  # Set this to the correct pin for the interrupt!
lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c, int1=int1)
clear = lambda: os.system('clear')
# Create a way to fade/transition between colors using numpy arrays

class MessageType(IntEnum):
	Close = 0;
	Init = 1;
	Input = 2;
	UserName = 3;

class Message:
	def __init__(self, message_type, message):
		self.message_type = message_type
		self.message = message

def accel_to_color(x, y, z):
    return (255/(abs(x)+1), 255/(abs(y) + 1), 255/(abs(z) + 1))


def fade(color1, color2, percent):
    color1 = np.array(color1)
    color2 = np.array(color2) 
    vector = color2-color1
    newcolor = (int((color1 + vector * percent)[0]), int((color1 + vector * percent)[1]), int((color1 + vector * percent)[2]))
    return newcolor


# Create a function that will cycle through the colors selected above
	
def rollcall_cycle(wait):
    for j in range(len(gokai_colors)):
        for i in range(10):
            color1 = gokai_colors[j]
            if j == 5:
                color2 = (255,255,255)
            else:
                color2 = gokai_colors[(j+1)]
            percent = i*0.1   # 0.1*100 so 10% increments between colors
            strip.fill((fade(color1,color2,percent)))
            strip.show()
            time.sleep(wait)

#strip.fill((255,0,0))
#strip.show()

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


def rollcall_cycle(wait):
    for j in range(len(gokai_colors)):
        for i in range(10):
            color1 = gokai_colors[j]
            if j == 5:
                color2 = (255,255,255)
            else:
                color2 = gokai_colors[(j+1)]
            percent = i*0.1   # 0.1*100 so 10% increments between colors
            strip.fill((fade(color1,color2,percent)))
            strip.show()
            time.sleep(wait)


def do_fade(color1, color2):
    for i in range(10):
        percent = i*0.1   # 0.1*100 so 10% increments between colors
        strip.fill((fade(color1,color2,percent)))
        strip.show()
        time.sleep(0.1)

def is_lamp_idle(sx, sy, sz):
    return sx < 0.3 or sy < 0.3 or sz < 0.3 

def calculate_idle(t):
    global STATE
    global prevColor
    x_arr = []
    y_arr = []
    z_arr = []
    while t >= 0:
        x, y, z = lis3dh.acceleration
        #print("Current colors")
        #print(accel_to_color(x,y,z))
        x_arr.append(x)
        y_arr.append(y)
        z_arr.append(z)
        newColor = accel_to_color(x,y,z)
        # remember prev color
        do_fade(prevColor, newColor)
        #strip.fill((int(a_x), int(a_y), int(a_z), 0))
        #strip.show()
        prevColor = newColor
        time.sleep(.2)
        t -= .2
    is_idle = is_lamp_idle(np.std(x_arr), np.std(y_arr), np.std(z_arr))
    
    if is_idle and STATE == "NOT IDLE" and CONNECTED:
        STATE = "IDLE"
        print("Sending color")
    elif is_idle and CONNECTED:
        # Check for data
        STATE = "IDLE"
        print ("Receiving data")
    elif is_idle and not CONNECTED:
        print ("Idle and not connected")
        STATE = "IDLE"
    else:
        STATE = "NOT IDLE"
        print("Is not idle")

    #print("numpy X_array", np.array(x_arr))
    #print("x std:", np.std(x_arr))
    #print("numpy Y_array", np.array(y_arr))
    #print("y std:", np.std(y_arr))
    #print("numpy Z_array", np.array(z_arr))
    #print("z std:", np.std(z_arr))

while True:
    # Comment this line out if you have RGBW/GRBW NeoPixels
 #   strip.fill((255, 0, 0))
    # Uncomment this line if you have RGBW/GRBW NeoPixels
    # pixels.fill((255, 0, 0, 0))
#    strip.show()
#    time.sleep(1)

    # Comment this line out if you have RGBW/GRBW NeoPixels
#    strip.fill((0, 255, 0))
    # Uncomment this line if you have RGBW/GRBW NeoPixels
    # pixels.fill((0, 255, 0, 0))
#    strip.show()
#    time.sleep(1)

    # Comment this line out if you have RGBW/GRBW NeoPixels
#    strip.fill((0, 0, 255))
    # Uncomment this line if you have RGBW/GRBW NeoPixels
    # pixels.fill((0, 0, 255, 0))
#    strip.show()
#    time.sleep(1)

#    rainbow_cycle(0.001)    # rainbow cycle with 1ms delay per step

# Calculate if light is idle
    calculate_idle(3)

#while True:

#    time.sleep(5)
	
#    rollcall_cycle(0.2)    # 0.2 seconds between color updates
