from multiprocessing import Process

class MavlinkComm(Process):

    def __init__(self, mavlink, queues):
        super(MavlinkComm, self).__init__()

        self.__mavlink = mavlink
        self.__queues = queues

    def run(self):

        while True:
            data = self.__mavlink.recv_match()
            message = data.data_to_dict()

            self.__queues.mavlink_nav.put(data)
            self.__queues.mavlink_depth.put(data)
