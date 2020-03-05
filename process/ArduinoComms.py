from multiprocessing import Process
class ArduinoComms(Process):

    def __init__(self, arduino, queues):
        super(ArduinoComms, self).__init__()
        self.arduino = arduino
        self.queues = queues
        self.__stopped = False

    def stop(self):
        print("stop")
        self.terminate()

    def run(self):

        # self.arduino

        while True:
            # print(self.arduino)
            try:
                message = self.queues.sendToArduino.get()
                arduino.sendMSG(message)
            except:
                pass

            if self.arduino.inWaiting() > 0:
                try:
                    dataRecvd = arduino.recv_from_arduino()
                    print(dataRecvd)
                    # print("Reply Received  " + dataRecvd)
                    arduino.process_arduino_data(dataRecvd)
                except:
                    # print("cannot read")
                    pass
