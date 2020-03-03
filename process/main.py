from pymavlink import mavutil
from multiprocessing import Process, Queue
import time
from sys import exit
import serial
import signal
from ProcessQueue import ProcessQueue
from DepthControllerProcess import DepthControllerProcess
from NavigateControllerProcess import NavigateControllerProcess
from HarvesterControllerProcess import HarvesterControllerProcess
from DriveObject import DriveObject
from DepthObject import DepthObject

from Arduino import Arduino
from ArduinoComm import ArduinoComm

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
    mavlink = mavutil.mavlink_connection('udpin:0.0.0.0:15000')
    # Wait a heartbeat before sending commands
    mavlink.wait_heartbeat()
    serial = serial.Serial('COM3', 115200, timeout=0)
    arduino = Arduino(serial, PING_FORWARD_STOP, PING_EXPIRE_TIME, PING_CONF)
    process_queues = ProcessQueue()
    depth_obj = DepthObject('', '')
    drive_obj = DriveObject('', '')
    arduino_comm = ArduinoComm
    depth_controller = DepthControllerProcess(depth_obj, mavlink, process_queues)
    nav_controller = NavigateControllerProcess(drive_obj, mavlink, process_queues)
    harv_controller = HarvesterControllerProcess(process_queues)
    armed = False ## processes only run when armed

    while True:
        if not armed:
            input_message = input('please arm the AUV')
            cmd_messages = input_message.split()
            cmd_message = cmd_messages[0]

            if cmd_message == 'arm':
                arm = True

                depth_controller.start()
                nav_controller.start()
                harv_controller.start()
                print('**AUV Armed**')
        else:
            input_message = input('Waiting For Command: ')
            cmd_messages = input_message.split()
            cmd_message = cmd_messages[0]

            if cmd_message == 'disarm':
                arm = False
                depth_controller.terminate()
                nav_controller.terminate()
                print('**AUV Disarmed**')
            if cmd_message == 'depth':
                msg = (cmd_message, 0)
                process_queues.ui_depth.put(msg)
            elif cmd_message == 'dive' or cmd_message == 'bottom_hold':
                msg = (cmd_message, float(cmd_messages[1]))
                process_queues.ui_depth.put(msg)
            elif cmd_message == 'forward':
                msg = ("straight", int(cmd_messages[1]), 1, float(cmd_messages[2]))
                process_queues.ui_nav.put(msg)
            elif cmd_message == 'backward':
                msg = ("straight", int(cmd_messages[1]), -1, float(cmd_messages[2]))
                process_queues.ui_nav.put(msg)
            elif cmd_message == 'yaw':
                dir = 1
                if float(cmd_messages[2]) < 0:
                    dir = -1
                msg = (cmd_messages, int(cmd_messages[1]), dir, abs(float(cmd_messages[2])))
                process_queues.ui_nav.put(msg)
            elif cmd_message == 'roomba':
                msg = (cmd_messages, float(cmd_messages[1]), 1, float(cmd_messages[2]))
                process_queues.ui_nav.put(msg)
            elif cmd_message == 'run mission':
                depth_msg = ("bottom_hold", float(1.5))
                nav_msg = ("roomba", float(30), 1, float(10000))
                process_queues.ui_depth.put(depth_msg)
                process_queues.ui_nav.put(nav_msg)
            elif cmd_message == 'help':
                print("arm - arm the motors")
                print("disarm - disarm the motors")
                print("yaw <0-100% throttle> <relative degrees> - turn robot")
                print("forward <0-100% throttle> <time in seconds> - drive forward for x seconds")
                print("reverse <0-100% throttle> <time in seconds> - drive reverse for x seconds")
                print("roomba <0-100% throttle> <time in seconds> - execute roomba search pattern for a given time")
                print("depth - enable depth hold mode")
                print("man - enable manual flight mode")
                print("dive <target depth (m)> - dive to given depth")
                print("bottomHold <0-100% throttle> <Distance from bottom(m)>")
                print("q - quit the program")
            elif cmd_message == 'quit' or cmd_message == 'q':
                depth_controller.terminate()
                nav_controller.terminate()
                harv_controller.start()
                break
        else:
            cmd_message = input('please arm the AUV')
            if cmd_message == 'arm':
                arm = True
                depth_controller.start()
                nav_controller.start()
                print('**AUV Armed**')