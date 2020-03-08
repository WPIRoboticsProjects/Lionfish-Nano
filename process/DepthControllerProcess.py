from multiprocessing import Process

class DepthControllerProcess(Process):

    def __init__(self, depth_obj, queues):
        super(DepthControllerProcess, self).__init__()
        self.__depth_obj = depth_obj
        self.__queues = queues

    def run(self):
        state = 'stop'
        mavlink_data = 0
        arduino_data = (0, 0)
        while True:
            buffer = 200#mm
            bottom_buffer = 2000
            throttle = 30
            desired_depth = 0
            # message will be a tuple,
            # bottom_hold or depth, depth value
            if not self.__queues.ui_depth.empty():
                message = self.__queues.ui_depth.get_nowait()
                print(message)
                state = message[0]
                desired_depth = message[1]  # depth => depth and bottom_hold => distance from bottom to hold
            else:
                pass

            if not self.__queues.arduino_depth.empty():
                mavlink_data = self.__queues.mavlink_depth.get_nowait()
            else:
                pass

            if not self.__queues.arduino_depth.empty():
                arduino_data = self.__queues.arduino_depth.get_nowait()
            else:
                pass

            if state == 'dive':
                current_depth = mavlink_data
                diff = current_depth - desired_depth
                print(current_depth, desired_depth, diff)
                if abs(diff) > buffer:
                        self.__depth_obj.decend(throttle, desired_depth, current_depth)
                else:
                    self.__depth_obj.clear_motors()
                    state ='stop'

            elif state == 'bottom_hold':
                current_depth = mavlink_data
                ping_distance = arduino_data[0]
                if (ping_distance < bottom_buffer and arduino_data[1] > 90):
                    self.__depth_obj.decend(throttle, (current_depth + (bottom_buffer - ping_distance)), current_depth)

                else:
                    self.__depth_obj.clear_motors()
                pass
            elif state == 'stop':
                self.__depth_obj.clear_motors()
                pass
