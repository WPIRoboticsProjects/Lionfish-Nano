import time
import queue

class Arduino:
    def __init__(self, serial):
        self.__serial = serial

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

    def object_forward(ping):
        if (ping < PING_FORWARD_STOP) and ping != -100:
            return True
        else:
            return False

    def ping_expire(ping_time):
        if (time.time() - ping_time) > PING_EXPIRE_TIME:
            return True
        else:
            return False

    def ping_conf(conf):
        if conf > PING_CONF:
            return True
        else:
            return False
