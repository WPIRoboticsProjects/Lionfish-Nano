from multiprocessing import Process

class TestComm(Process):

    def __init__(self, queues):
        super(TestComm, self).__init__()

        self.__queues = queues

    def run(self):
        print("TESTCOMM")
        message = self.__queues.mavlink_nav.get_nowait()
        if not message:
            continue
        print(message)