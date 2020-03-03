import time
import queue

class Arduino:
    def __init__(self, serial, forward_stop, expire_time, conf):
        self.__serial = serial
        self.__forward_stop = forward_stop
        self.__expire_time = expire_time
        self.__conf = conf

        pass

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


