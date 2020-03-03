from pymavlink import mavutil
from multiprocessing import Process, Queue
import time
from sys import exit
import serial
import signal
import random
import math

def handler(signum, frame):
    print('Handle Ctrl-C')
    handle_exit()
    exit()

def handle_exit():
    print("Exiting")
    exit()

def run(master, qFromArduino, qToArduino):
    main_loop_queue = Queue()
    main_loop_process = Process(target=main_loop, args=(master, main_loop_queue, qFromArduino, qToArduino,))
    #main_loop_process.daemon = True
    main_loop_process.start()

    cont_run = True
    while cont_run:
        command = input("Command: ")
        main_loop_queue.put(command)
        
        commands = command.split()
        verb = lookup_button(commands[0])
        if verb == -2:
            handle_exit()
        time.sleep(1)

def main_loop(master, main_loop_queue, qFromArduino, qToArduino):

    cmd_queue = Queue()

    forward_ping = -100
    forward_ping_time = 0
    forward_ping_conf = 0
    down_ping = -100
    down_ping_time = 0
    down_ping_conf = 0
    ping1, ping1_conf, ping2, ping2_conf = update_sensors(qFromArduino)

    
    if ping1 != -100:
        forward_ping = ping1
        forward_ping_conf = ping1_conf
        forward_ping_time = time.time()
        # sensor 0, data, time taken
        cmd_queue.put((0, forward_ping, forward_ping_time, ping1_conf))
    if ping2 != -100:
        down_ping = ping2
        down_ping_conf = ping2_conf
        down_ping_time = time.time()
        # sensor 0, data, time taken
        cmd_queue.put((1, down_ping, down_ping_time, ping2_conf))

    cont_run = True
    while cont_run:
        try:

            if not main_loop_queue.empty():
                command = main_loop_queue.get()
                print("Given command: " + command + "\n")
                commands = command.split()
                verb = lookup_button(commands[0])
                if verb == -2:
                    handle_exit()

                if verb == 101:
                    if commands[1] == '1':
                        print("forward ping: " + str(forward_ping) + " mm,   conf: " + str(forward_ping_conf))
                        print("forward ping: " + str((forward_ping/25.4)) + " inches,   conf: " + str(forward_ping_conf))
                    elif commands[1] == '2':
                        print("down ping: " + str(down_ping) + " mm,   conf: " + str(down_ping_conf))
                        print("forward ping: " + str((down_ping / 25.4)) + " inches,   conf: " + str(down_ping_conf))
                
                if verb != -1:
                    motor_cmd_process = Process(target=motor_cmd, args=(master, verb, commands, cmd_queue))
                    motor_cmd_process.daemon = True
                    motor_cmd_process.start()
                else:
                    print("Unknown command, list of available commands: \n")
                    print_cmd_list()
                    print("")

            # update sensors
            ping1, ping1_conf, ping2, ping2_conf = update_sensors(qFromArduino)
            if ping1 != -100:
                forward_ping = ping1
                forward_ping_conf = ping1_conf
                cmd_queue.put((0, forward_ping, forward_ping_time, ping1_conf))
            if ping2 != -100:
                down_ping = ping2
                down_ping_conf = ping2_conf
                cmd_queue.put((1, down_ping, down_ping_time, ping2_conf))

        except Exception as e:
            print("Incorrect command: " + str(e))
            exit()



def lookup_button(string_in):
    if string_in == "depth":
        return 0
    elif string_in == "stab":
        return 1
    elif string_in == "man":
        return 2
    elif string_in == "disarm":
        return 4
    elif string_in == "arm":
        return 6
    elif string_in == "lights":
        return 9
    elif string_in == "hold":
        return 10
    elif string_in == "camdown":
        return 11
    elif string_in == "camup":
        return 12
    elif string_in == "yaw":
        return 13
    elif string_in == "forward":
        return 14
    elif string_in == "reverse":
        return 15
    elif string_in == "dive":
        return 16
    elif string_in == "square":
        return 17
    elif string_in == "bottomHold":
        return 18
    elif string_in == "roomba":
        return 19
    elif string_in == "xyzNav":
        return 20
    elif string_in == "hud":
        return 100
    elif string_in == "ping":
        return 101
    elif string_in == "quit":
        return -2
    elif string_in == "q":
        return -2
    else:
        return -1

def print_cmd_list():
    print("arm - arm the motors")
    print("disarm - disarm the motors")
    print("depth - depth mode")
    print("stab - stabilize mode")
    print("man - manual mode")
    print("lights - toggle lights")
    print("hold - hold last sent command")
    print("camdown - move camera down")
    print("camup - move camera up")
    print("yaw <0-100% throttle> <relative degrees> - turn robot")
    print("forward <0-100% throttle> <time in seconds> - drive forward for x seconds")
    print("reverse <0-100% throttle> <time in seconds> - drive reverse for x seconds")
    print("dive <0-100% throttle> <target depth (m)> - dive to given depth")
    print("square - travel in a rectangle")
    print("roomba <0-100% throttle> <time in seconds> - execute roomba search pattern for a given time")
    print("xyzNav <time in seconds> <0-100% throttle> <Relative X> <Relative Y> <Relative Z>- Move to a relative XYZ position")
    print("bottomHold <time in seconds> <0-100% throttle> <Distance from bottom(M)>")
    print("hud - print out the hud data")
    print("ping <ID> - return ping data from given ID, start at 1")
    print("square - run a rectangle")
    print("q - quit the program")
