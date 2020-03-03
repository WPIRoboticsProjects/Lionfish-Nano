from multiprocessing import Process

class TestComm(Process):

    def __init__(self, queues):
        super(TestComm, self).__init__()

        self.__queues = queues

    def run(self):
        print("TESTCOMM")
        while True:
            print(self.__queues.arduino_nav.qsize())
            message = self.__queues.arduino_nav.get()
            print(message)
