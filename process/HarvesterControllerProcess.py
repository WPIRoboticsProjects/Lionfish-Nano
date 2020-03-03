from multiprocessing import Process
import time


class HarvesterControllerProcess(Process):
    def __init__(self, harv_obj, queues):
        super(HarvesterControllerProcess, self).__init__()
        self.__harv_obj = harv_obj
        self.__queues = queues

    def run(self):
        spearArmed = False

        while True:
            try:
                msg = self.__queues.harv_comms.get()
                if msg[0] == 'arm':
                    spearArmed = True
                    #extend spear
                elif msg[0] == 'fire' and spearArmed:
                    #shoot spear
                    pass
                else:
                    pass
            except:
                pass
