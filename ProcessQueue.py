from multiprocessing import Queue

'''
Author: Harrison Saperstein
Description: Class that handles all queues passed between processes. Now one object can be passed 
for all processed to access all needed queues
'''
class ProcessQueue:
    def __init__(self):
        self.qToArduino = Queue()
        self.qFromArduino = Queue()