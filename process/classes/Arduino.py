import time
import queue

class Arduino:
    def __init__(self, serial, forward_stop, expire_time, conf):
        self.__serial = serial
        self.__forward_stop = forward_stop
        self.__expire_time = expire_time
        self.__conf = conf
        self.__start_marker = '<'
        self.__end_marker = '>'

        pass

    def is_waiting(self):
        return self.__serial.inWaiting()

    def check_sensors(self, q):

        ping1_val = -100
        ping1_time = 0
        ping1_conf = 0
        ping2_val = -100
        ping2_time = 0
        ping2_conf = 0
        if not q.empty():
            val = q.get()
            if val[0] == 0:
                ping1_val = val[1]
                ping1_time = val[2]
                ping1_conf = val[3]
            elif val[0] == 1:
                ping2_val = val[1]
                ping2_time = val[2]
                ping2_conf = val[3]

            for i in range(q.qsize()):
                val = q.get()
                if val[0] == 0:
                    ping1_val = val[1]
                    ping1_time = val[2]
                    ping1_conf = val[3]
                elif val[0] == 1:
                    ping2_val = val[1]
                    ping2_time = val[2]
                    ping2_conf = val[3]
        return ping1_val, ping1_time, ping1_conf, ping2_val, ping2_time, ping2_conf

    def process_arduino_data(self, message, queues):
        recvMessage = message.split()
        messType = int(recvMessage[1])
        # 0: ping
        # 1: none
        # 2: battery
        # 3: leak

        messId = int(recvMessage[2])
        # 1: front or down
        # 2: front or down

        messData = int(recvMessage[3])
        confData = int(recvMessage[4])

        # print("Type: " + str(messType) + ", id: " + str(messId) + ", data: " + str(messData))
        if messType == 0:
            if messId == 1:
                queues.arduino_nav.put((messData, confData))
            elif messId == 2:
                queues.arduino_depth.put((messData, confData))
            # ping sensor update
            # qFromArduino # send received data to jetson
        elif messType == 1:
            pass
            # spear move update
        # elif messType == 2:  # BATTERY
        #     if messId == 1:  # VOLTAGE
        #         queues.qFromArduino.put((2, messData, confData))
        #     elif messId == 2:  # CURRENT
        #         queues.qFromArduino.put((3, messData, confData))
        # elif messType == 3:  # leak
        #     print("**************SOS - LEAK DETECTED**************")
        #     self.queues.qFromArduino.put((4, messData, confData))
        #     print("**************SOS - LEAK DETECTED**************")

    def recv_from_arduino(self):

        ck = ""
        x = "z"  # any value that is not an end- or startMarker
        byteCount = -1  # to allow for the fact that the last increment will be one too many

        # wait for the start character
        while ord(x) != self.__start_marker:
            x = self.__serial.read()

        # save data until the end marker is found
        while ord(x) != self.__end_marker:
            if ord(x) != self.__start_marker:
                ck = ck + x.decode("utf-8")
                byteCount += 1
            x = self.__serial.read()

    def object_forward(self, ping):
        if (ping < self.__forward_stop) and ping != -100:
            return True
        else:
            return False

    def ping_expire(self, ping_time):
        if (time.time() - ping_time) > self.__expire_time:
            return True
        else:
            return False

    def ping_conf(self, conf):
        if conf > self.__conf:
            return True
        else:
            return False


