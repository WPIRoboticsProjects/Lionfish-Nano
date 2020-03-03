from multiprocessing import Process

class DepthControllerProcess(Process):

    def __init__(self, depth_obj, queues):
        super(DepthControllerProcess, self).__init__()
        self.__depth_obj = depth_obj
        self.__queues = queues

    def run(self):

        while True:
            # message will be a tuple,
            # bottom_hold or depth, depth value
            message = self.__queues.ui_depth.get()
            print(message)
            state = message[0]
            depth = message[1]
            if state == 'bottom_hold':
                self.__depth_obj.hold_test(depth)
            elif state == 'depth':
                self.__depth_obj.depth_test(depth)
