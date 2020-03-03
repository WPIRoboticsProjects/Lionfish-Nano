from multiprocessing import Process
class ArduinoComm(Process):

    def __init__(self, arduino, queues):
        super(ArduinoComm, self).__init__()
        self.__arduino = arduino
        self.__queues = queues
        self.__stopped = False

    def run(self):

        while True:

            # todo get processed data from arduino
            #  and print it

            if self.__arduino.is_waiting() > 0:
                try:
                    data = self.__arduino.recv_from_arduino()
                    # print("Reply Received  " + dataRecvd)
                    self.__arduino.process_arduino_data(data, self.__queues)
                except:
                    # print("cannot read")
                    pass

