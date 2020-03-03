import time
import numpy as np
class DepthObject:
    def __init__(self, mavlink, turn_buffer):
        self.mavlink = mavlink
        self.turn_buffer = turn_buffer
        # self.msg_handle = msg_handle

    def write_pwm(self, output_channel, output_val):
        rc_channel_values = [65535 for _ in range(8)]
        rc_channel_values[output_channel] = output_val
        self.mavlink.mav.rc_channels_override_send(
            self.mavlink.target_system,  # target_system
            self.mavlink.target_component,  # target_component
            *rc_channel_values)

    def clear_motors(self):
        rc_channel_values = [0 for _ in range(8)]
        self.mavlink.mav.rc_channels_override_send(
            self.mavlink.target_system,  # target_system
            self.mavlink.target_component,  # target_component
            *rc_channel_values)

       # to certain distance
    def depth_test(self, throttle, target_depth, currentDepth):
        if 0 < throttle <= 100:
            diff = target_depth - currentDepth
            if diff < 0: #too high 
                output = (-throttle * 5) + 1500#go down
            elif diff > 0:# too low
                output = (throttle * 5) + 1500#go up
            self.write_pwm( 2, output)
        elif throttle == 0:
            self.write_pwm(2, 0)
