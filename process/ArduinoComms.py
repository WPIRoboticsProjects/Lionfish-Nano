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
            print(self.arduino)
            try:
                message = self.queues.sendToArduino.get()
                sendMSG(message)
            except:
                pass

            if self.arduino.inWaiting() > 0:
                try:
                    dataRecvd = self.recv_from_arduino()
                    # print("Reply Received  " + dataRecvd)
                    self.process_arduino_data(dataRecvd)
                except:
                    # print("cannot read")
                    pass

    def sendMSG(self, message):
        if type(message) == 'char':
            self.arduino.serial.write(message).encode('utf-8')
        else:
            #wrong data type
            pass


    def process_arduino_data(self, message):
        recvMessage = message.split()
        messType = int(recvMessage[1])
        messId = int(recvMessage[2])
        messData = int(recvMessage[3])
        confData = int(recvMessage[4])

        # print("Type: " + str(messType) + ", id: " + str(messId) + ", data: " + str(messData))
        if messType == 0:
            if messId == 1:
                self.queues.qFromArduino.put((0, messData, confData))
            elif messId == 2:
                self.queues.qFromArduino.put((1, messData, confData))
            # ping sensor update
            # qFromArduino # send received data to jetson
        elif messType == 1:
            pass
            # spear move update
        elif messType == 2:  # BATTERY
            if messId == 1:  # VOLTAGE
                self.queues.qFromArduino.put((2, messData, confData))
            elif messId == 2:  # CURRENT
                self.queues.qFromArduino.put((3, messData, confData))
        elif messType == 3:  # leak
            print("**************SOS - LEAK DETECTED**************")
            self.queues.qFromArduino.put((4, messData, confData))
            print("**************SOS - LEAK DETECTED**************")

    def recv_from_arduino(self):
        # todo pass these in somehow
        global startMarker, endMarker


        # todo wtf are these
        ck = ""
        x = "z"  # any value that is not an end- or startMarker
        byteCount = -1  # to allow for the fact that the last increment will be one too many

        # wait for the start character
        while ord(x) != startMarker:
            x = self.arduino.read()

        # save data until the end marker is found
        try: 
            while ord(x) != endMarker:
                if ord(x) != startMarker:
                    ck = ck + x.decode("utf-8")
                    byteCount += 1
                x = self.arduino.read()
        
        except:
            print("serial Corruption Detected: setting message to default")
            x = ""

        return x
