from multiprocessing import Process
import time
class MavlinkComm(Process):

    def __init__(self, mavlink, queues):
        super(MavlinkComm, self).__init__()

        self.__mavlink = mavlink
        self.__queues = queues

    def run(self):

        while True:
            # print("here")
            data = self.__mavlink.recv_match()
            # print('/ data')
            if not data:
                continue
            # if data.get_type() == 'VFR_HUD':

            message = data.to_dict()
            # print("MAVCOM: ", message)
            self.__queues.mavlink_nav.put(message)
            print(self.__queues.mavlink_nav.qsize())
                # self.__queues.mavlink_depth.put(message)
            # time.sleep(2)