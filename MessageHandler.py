'''
this class creates a message handler object to perform message passing and parsing
operations
'''

class MessageHandler:
    def __init__(self, mavlink):
        self.mavlink = mavlink



    def get_message(self):
        while True:
            msg = self.mavlink.recv_match()
            if not msg:
                continue
            # print(msg.get_type())
            if msg.get_type() == 'VFR_HUD':
                # print("\n\n*****Got message: %s*****" % msg.get_type())
                # print("Message: %s" % msg)
                # print("\nAs dictionary: %s" % msg.to_dict())
                return msg.to_dict()
