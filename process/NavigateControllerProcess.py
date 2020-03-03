from multiprocessing import Process
import time


class NavigateControllerProcess(Process):
    def __init__(self, nav_obj, mavlink, queues):
        super(NavigateControllerProcess, self).__init__()
        self.__nav_obj = nav_obj
        self.__queues = queues
        self.__mavlink = mavlink

    def run(self):
        minObjectDistance = 2000
        start_time = time.time()
        last_message = ''
        current_heading = 0
        original_heading = current_heading
        state = ''
        throttle = 0
        direction = 0
        desired_amount = 0
        roomba_state = 'straight'
        while True:

            # todo: add in no wait if empty queues (prob in ProcessQueues class)
            new_message = self.__queues.ui_nav.get()
            sensor_data = self.__queues.sensor_data.get()

            # todo: probably better to make a process that pulls mavlink data
            #  and parses it into message queues
            mavlink_data = self.__mavlink.recv_match()

            # todo: make better standard messages for cmd passing and such,
            #  tuples for now
            if not last_message[0] == new_message[0]:
                state = new_message[0]
                throttle = new_message[1]
                direction = new_message[2]
                desired_amount = new_message[3]  # time or angle

                if not mavlink_data:
                    pass
                elif mavlink_data.get_type() == 'VFR_HUD':
                    original_heading = mavlink_data.to_dict()['heading']
                else:
                    pass

                start_time = time.time()

            if state == 'straight':
                current_time = time.time()
                drive_time = current_time - start_time
                if drive_time <= desired_amount:
                    self.__nav_obj.drive_straight(throttle, direction)
                else:
                    self.__nav_obj.clear_motors()
                    last_message = new_message
                    state = 'stop'

            elif state == 'turn':
                if not mavlink_data:
                    continue
                elif mavlink_data.get_type() == 'VFR_HUD':
                    current_heading = mavlink_data.to_dict()['heading']
                else:
                    continue
                desired_rel_angle = direction * desired_amount
                if self.__nav_obj.continue_turn(original_heading, current_heading, desired_rel_angle):
                    self.__nav_obj.turn(throttle, desired_rel_angle)
                else:
                    last_message = new_message
                    self.__nav_obj.clear_motors()
                    state = 'stop'

            elif state == 'roomba':
                if roomba_state == 'straight':
                    if(sensor_data[0] > minObjectDistance):
                        self.__nav_obj.drive_straight(throttle, 1)
                    else:
                        roomba_state = 'turn'

                elif roomba_state == 'turn':
                    if not mavlink_data:
                        continue
                    elif mavlink_data.get_type() == 'VFR_HUD':
                        current_heading = mavlink_data.to_dict()['heading']
                    else:
                        continue

                    if(self.__nav_obj.continue_turn(original_heading, current_heading, 100)):
                        self.__nav_obj.turn(throttle, desired_rel_angle)
                    else:
                        self.__nav_obj.clear_motors()
                        roomba_state = 'straight'
                else:
                    pass
            
            elif state == 'lionfish':
                pass
            elif state == 'stop':
                self.__nav_obj.clear_motors()