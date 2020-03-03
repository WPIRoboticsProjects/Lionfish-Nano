from multiprocessing import Process

class DepthControllerProcess(Process):

    def __init__(self, depth_obj, mavlink, queues):
        super(DepthControllerProcess, self).__init__()
        self.__depth_obj = depth_obj
        self.__queues = queues
        self.__mavlink = mavlink

    def run(self):

        while True:
            buffer = 200#mm
            throttle = 30
            desired_depth = 0
            # message will be a tuple,
            # bottom_hold or depth, depth value
            message = self.__queues.ui_depth.get()
            sensors = self.__queues.sensor_data.get()
            print(message)
            state = message[0]
            uiData = message[1] #depth => depth and bottom_hold => distance from bottom to hold

            mavlink_data = self.__mavlink.recv_match()
            if not mavlink_data:
                pass
            elif mavlink_data.get_type() == 'VFR_HUD':
                altitude = mavlink_data.to_dict()['alt']#auv's depth reading
            else:
                pass


            if state == 'bottom_hold':
                diff = sensors[2] - uiData*1000#mm - m * 1000
                if diff > abs(buffer):#need to adjust
                    if diff > 0:#too high
                        self.__depth_obj.depth_test(throttle, desired_depth - diff, altitude)
                    elif diff < 0:# too low
                        self.__depth_obj.depth_test(throttle, desired_depth - diff, altitude)
                    else:#error catching
                        pass
                else:#no need to adjust
                    pass

            elif state == 'dive':
                desired_depth = uiData
                diff = altitude - desired_depth
                if abs(diff) > buffer:
                        self.__depth_obj.depth_test(throttle, desired_depth, altitude)
                else:
                    pass