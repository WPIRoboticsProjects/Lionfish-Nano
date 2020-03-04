from multiprocessing import Process

class TestComm(Process):

    def __init__(self, queues, debug=False):
        super(TestComm, self).__init__()

        self.__queues = queues
        self.__debug = debug

    def run(self):
        print("TESTCOMM")
        if not self.__debug:
            while True:
                arduino = self.__queues.arduino_test.get()
                mavlink = self.__queues.mavlink_test.get()
                print(arduino)
                print(mavlink)
