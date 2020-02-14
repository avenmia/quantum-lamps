import time
import board
import digitalio
import busio
import adafruit_lis3dh
import os

def accel_to_color(x, y, z):
    return (255/(abs(x)+1), 255/(abs(y) + 1), 255/(abs(z) + 1))



i2c = busio.I2C(board.SCL, board.SDA)
int1 = digitalio.DigitalInOut(board.D6)  # Set this to the correct pin for the interrupt!
lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c, int1=int1)
clear = lambda: os.system('clear')
while True:
    x, y, z = lis3dh.acceleration
    clear()
    print("Current colors")
    print(accel_to_color(x,y,z))
    time.sleep(0.3)
