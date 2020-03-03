from multiprocessing import Process
import time


class HarvesterControllerProcess(Process):
    def __init__(self, queues):
        super(HarvesterControllerProcess, self).__init__()
        self.__queues = queues

    def run(self):
        spearArmed = False
        state = 'disarmed'

        while True:
            try:
                msg = self.__queues.harv_comms.get()
                if msg[0] == 'arm':
                    state = 'arming'
                elif msg[0] == 'fire':
                    state = 'Trying To Fire'
                elif msg[0] == 'disarm':
                    spearArmed = False
                    state = 'disarming'
                else:
                    pass

                if state == 'arming':
                    self.__queues.toArduinoQ.put('a')# arm
                    print('CAUTION SPEAR ARMED!!!')
                    state = 'armed'
                    spearArmed = True

                elif state == 'Trying To Fire' and not spearArmed:
                    print('Arm Spear Before Firing')
                elif state == 'Trying To Fire' and spearArmed:
                    self.__queues.toArduinoQ.put('f')# fire
                    state = 'fired'

                elif state == 'fired':
                    #check for fish
                    #put away spear
                    pass

                elif state == 'disarming':
                    self.__queues.toArduinoQ.put('d')# disarm
                    state = 'disarmed'
                    spearArmed = False
                    print('Spear Disarmed.')
            except:
                pass
