import time
import numpy as np
class DriveObject:
    def __init__(self, mavlink, turn_buffer):
        self.mavlink = mavlink
        self.turn_buffer = turn_buffer
        self.original_heading = 0
        # self.msg_handle = msg_handle

    def write_pwm(self, output_channel, output_val):
        rc_channel_values = [65535 for _ in range(8)]
        rc_channel_values[output_channel] = output_val
        self.mavlink.mav.rc_channels_override_send(
            self.mavlink.target_system,  # target_system
            self.mavlink.target_component,  # target_component
            *rc_channel_values)

    def clear_motors(self):
        rc_channel_values = [65535 for _ in range(8)]
        self.mavlink.mav.rc_channels_override_send(
            self.mavlink.target_system,  # target_system
            self.mavlink.target_component,  # target_component
            *rc_channel_values)

    def drive_straight(self, throttle, direction):
        # direction:
        #  1: forward
        # -1: backward
        output = (direction * throttle * 5) + 1500
        self.write_pwm(4, output)

    def is_turn_finished(self, curr_heading, rel_angle):

        final_heading = self.original_heading + rel_angle
        if final_heading > 360:
            final_heading -= 360
        if final_heading < 0:
            final_heading += 360

        if (final_heading + self.turn_buffer) > 360:
            if abs(final_heading - 360 - curr_heading) < self.turn_buffer:
                return False
        if (final_heading - self.turn_buffer) < 0:
            if abs(final_heading + 360 - curr_heading) < self.turn_buffer:
                return False
        if abs(final_heading - curr_heading) < self.turn_buffer:
            return False
        else:
            return True

    def turn(self, throttle, angle):
        # -1: Port
        #  1: Starboard
        direction = np.sign(angle)
        output = (direction*throttle * 5) + 1500

        self.write_pwm(3, output)
