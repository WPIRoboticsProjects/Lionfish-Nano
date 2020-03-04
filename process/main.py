from pymavlink import mavutil
import numpy as np
import serial
import signal
from DepthControllerProcess import DepthControllerProcess
from NavigateControllerProcess import NavigateControllerProcess
from MavlinkComm import MavlinkComm
from classes.ProcessQueue import ProcessQueue
from classes.DriveObject import DriveObject
from classes.DepthObject import DepthObject
from classes.Arduino import Arduino
from HarvesterControllerProcess import HarvesterControllerProcess
from ArduinoComm import ArduinoComm


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


def handler(signum, frame):
    print('Handle Ctrl-C')
    handle_exit()
    exit()

def handle_exit():
    print("Exiting")
    exit()

if __name__=='__main__':
    process_queues = ProcessQueue()
    signal.signal(signal.SIGINT, handler)

    mavlink = mavutil.mavlink_connection('udpin:0.0.0.0:15000')
    mavlink.wait_heartbeat() # Wait a heartbeat before sending commands
    mavlink_comm = MavlinkComm(mavlink, process_queues)

    serial_connection = serial.Serial("/dev/serial/by-path/platform-70090000.xusb-usb-0:2.2:1.0", 115200, timeout=0)
    arduino = Arduino(serial_connection, PING_FORWARD_STOP, PING_EXPIRE_TIME, PING_CONF)
    arduino_comm = ArduinoComm(arduino, process_queues)

    # depth_obj = DepthObject('', '')
    # depth_controller = DepthControllerProcess(depth_obj, process_queues)

    drive_obj = DriveObject(mavlink, TURN_BUFFER)
    nav_controller = NavigateControllerProcess(drive_obj, process_queues)

    harv_controller = HarvesterControllerProcess(process_queues)

    armed = False ## processes only run when armed

    while True:
        if not armed:
            cmd_message = input('please arm the AUV')
            if cmd_message == 'arm':
                armed = True
                arm = 1 << 6
                mavlink.mav.manual_control_send(mavlink.target_system, 0, 0, 0, 0, arm)
                # depth_controller.start()
                nav_controller.start()
                harv_controller.start()
                print('**AUV Armed**')
        else:
            input_message = input('Waiting For Command: ')
            cmd_messages = input_message.split()
            cmd_message = cmd_messages[0]

            if cmd_message == 'disarm':
                arm = False
                # depth_controller.terminate()
                nav_controller.terminate()

                # todo clean up and make sure harvester is disarmed
                #  at the arduino before termination
                harv_controller.terminate()
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

            elif cmd_message == 'turn' or cmd_message == 'yaw':
                msg = ('turn', int(cmd_messages[1]), np.sign(int(cmd_messages[2])), abs(float(cmd_messages[2])))
                process_queues.ui_nav.put(msg)

            # elif cmd_message == 'roomba':
            #     msg = (cmd_messages, float(cmd_messages[1]), 1, float(cmd_messages[2]))
            #     process_queues.ui_nav.put(msg)
            # elif cmd_message == 'run mission':
            #     depth_msg = ("bottom_hold", float(1.5))
            #     nav_msg = ("roomba", float(30), 1, float(10000))
            #     process_queues.ui_depth.put(depth_msg)
            #     process_queues.ui_nav.put(nav_msg)
            elif cmd_message == 'stop':
                process_queues.ui_nav.put((cmd_message, 0, 0, 0))
                process_queues.ui_depth.put((cmd_message, 0))

            elif cmd_message == 'help':
                print("arm - arm the motors")
                print("disarm - disarm the motors")
                print("turn|yaw <0-100% throttle> <relative degrees> - turn robot")
                print("forward <0-100% throttle> <seconds> - drive forward for x seconds")
                print("reverse <0-100% throttle> <seconds> - drive reverse for x seconds")
                print("roomba <0-100% throttle> - execute roomba search pattern for a given time")
                print("depth <0-100% throttle> <target depth (m)> - dive to given depth")
                print("bottomHold <0-100% throttle> <Distance from bottom(m)>")
                print("q - quit the program")
            elif cmd_message == 'quit' or cmd_message == 'q':
                # depth_controller.terminate()
                nav_controller.terminate()
                harv_controller.terminate()
                arduino_comm.terminate()
                mavlink_comm.terminate()
                break