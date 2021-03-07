from __future__ import print_function
from flask import Flask
from redis import Redis
import time 
from serial.tools import list_ports
import serial
import re
import os
import io
from pyax12.connection import Connection        


app = Flask(__name__)
redis = Redis(host='redis', port=6379)

def motor_move(serial_connection, dynamixel_id):
    serial_connection.goto(dynamixel_id, 0, speed=512, degrees=True)
    time.sleep(1)    # Wait 1 second

    # Go to -45° (45° CW)
    serial_connection.goto(dynamixel_id, -45, speed=512, degrees=True)
    time.sleep(1)    # Wait 1 second

    # Go to -90° (90° CW)
    serial_connection.goto(dynamixel_id, -90, speed=512, degrees=True)
    time.sleep(1)    # Wait 1 second

    # Go to -135° (135° CW)
    serial_connection.goto(dynamixel_id, -135, speed=512, degrees=True)
    time.sleep(1)    # Wait 1 second

    # Go to -150° (150° CW)
    serial_connection.goto(dynamixel_id, -150, speed=512, degrees=True)
    time.sleep(1)    # Wait 1 second

    # Go to +150° (150° CCW)
    serial_connection.goto(dynamixel_id, 150, speed=512, degrees=True)
    time.sleep(2)    # Wait 2 seconds

    # Go to +135° (135° CCW)
    serial_connection.goto(dynamixel_id, 135, speed=512, degrees=True)
    time.sleep(1)    # Wait 1 second

    # Go to +90° (90° CCW)
    serial_connection.goto(dynamixel_id, 90, speed=512, degrees=True)
    time.sleep(1)    # Wait 1 second

    # Go to +45° (45° CCW)
    serial_connection.goto(dynamixel_id, 45, speed=512, degrees=True)
    time.sleep(1)    # Wait 1 second

    # Go back to 0°
    serial_connection.goto(dynamixel_id, 0, speed=512, degrees=True)

    

@app.route('/')
def hello():
    # Connect to the serial port
    serial_connection = Connection(port="/dev/ttyUSB0", baudrate=1000000)
    is_available0 = serial_connection.ping(0)
    is_available1 = serial_connection.ping(1)
    motor_move(serial_connection, 1)
    motor_move(serial_connection, 0)
    serial_connection.close()
    return "motor 0 : {}, motor 1: {}".format(is_available0, is_available1)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
