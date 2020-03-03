from multiprocessing import Queue

'''
Author: Harrison Saperstein
Description: Class that handles all queues passed between processes. Now one object can be passed 
for all processed to access all needed queues
'''
class ProcessQueue:
    def __init__(self):
        # self.sensor_data = Queue()# 0-ping1 1- ping1conf 2- ping2 3- ping3conf
        self.mavlink_nav = Queue()
        self.mavlink_depth = Queue()
        self.arduino_nav = Queue()
        self.arduino_depth = Queue()
        self.ui_nav = Queue()
        self.ui_depth = Queue()
        self.harv_comms = Queue()
        self.toArduinoQ = Queue()

