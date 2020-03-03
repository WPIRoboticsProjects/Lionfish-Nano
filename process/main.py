from pymavlink import mavutil
from multiprocessing import Process, Queue
import time
from sys import exit
import serial
import signal
from ProcessQueue import ProcessQueue
from Arduino import Arduino
from ArduinoComms import *

import random
import math

# Pwm channel pins
# 0 - pitch
# 1 - roll
# 2 - up
# 3 - yaw
# 4 - forward
# 5 - lateral
# 6 - camera pan
# 7 - camera tilt
# 8 - lights 1 level


TURN_BUFFER = 2
PING_FORWARD_STOP = 2000
PING_EXPIRE_TIME = 3 # seconds
PING_CONF = 60

startMarker = 60
endMarker = 62

def handler(signum, frame):
    print('Handle Ctrl-C')
    handle_exit()
    exit()

def handle_exit():
    print("Exiting")
    exit()

if __name__=='__main__':
    signal.signal(signal.SIGINT, handler)

    process_queues = ProcessQueue()
    mavlink = mavutil.mavlink_connection('udpin:0.0.0.0:15000')
    # Wait a heartbeat before sending commands
    mavlink.wait_heartbeat()
    serial = serial.Serial('COM3', 115200, timeout=0)
    arduino = Arduino(serial)
    arduino_comm = ArduinoComms(arduino, 'test')


    # STATE SPACE::
    # While scanning for lionfish
        # Roomba process
    # if see lionfish
        # movre toward lionfish
    # if emergence kill lionfish and roomba search
    # if end of mission go home
    arduino_comm.start()
    print('here')
    time.sleep(10)
    arduino_comm.terminate()
    print("process_stopped")
    # Create the connection
    mavlink = mavutil.mavlink_connection('udpin:0.0.0.0:15000')
    # Wait a heartbeat before sending commands
    mavlink.wait_heartbeat()


    #Start arduino Process
    #start camera process,
        # including object detection and tracking processes

