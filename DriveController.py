import time
from MessageHandler import *
class DriveController:
    def __init__(self, mavlink, turn_buffer, msg_handle):
        self.mavlink = mavlink
        self.turn_buffer = turn_buffer
        self.msg_handle = msg_handle

    def write_pwm(self, output_channel, output_val):
        rc_channel_values = [65535 for _ in range(8)]
        rc_channel_values[output_channel] = output_val
        self.mavlink.mav.rc_channels_override_send(
            self.mavlink.target_system,  # target_system
            self.mavlink.target_component,  # target_component
            *rc_channel_values)

    def drive_forward(self, val, time_to_drive):
        '''

        :param master: mavlink connection
        :param val:
        :param time_to_drive:
        :return:
        '''
        if val > 0 and val <= 100:
            output = (val * 5) + 1500
            end_time = time.time() + time_to_drive
            while time.time() < end_time:
                self.write_pwm( 4, output)

    def drive_backward(self, val, time_to_drive):
        if val > 0 and val <= 100:
            output = (-val * 5) + 1500
            end_time = time.time() + time_to_drive
            while time.time() < end_time:
                self.write_pwm(4, output)

    def continue_turn(self, org_heading, curr_heading, rel_angle):

        final_heading = org_heading + rel_angle
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

    def turn_angle(self, val, rel_angle):
        if val > 0 and val <= 100:
            output = (val * 5) + 1500
            if rel_angle < 0:
                output = (-val * 5) + 1500

            org_heading = float(self.msg_handle.get_message(self.mavlink)['heading'])
            curr_heading = org_heading

            while self.continue_turn(org_heading, curr_heading, rel_angle):
                self.write_pwm(3, output)
                curr_heading = float(self.msg_handle.get_message(self.mavlink)['heading'])

        elif val == 0:
            self.write_pwm( 3, 0)

    def depth(self, val, target_depth):
        if val > 0 and val <= 100:
            curr_depth = float(self.msg_handle.get_message(self.mavlink)['alt'])
            output = (val * 5) + 1500
            if (target_depth - curr_depth) < 0:
                output = (-val * 5) + 1500

            while abs(target_depth - curr_depth) > 0.2:
                self.write_pwm( 2, output)
                curr_depth = float(self.msg_handle.get_message(self.mavlink)['alt'])
        elif val == 0:
            self.write_pwm(2, 0)

    def bottom_hold(self, in_time, throttle, target_distance, cmd_queue):
        end_time = time.time() + in_time

        ping1_ret, ping1_time_ret, ping1_conf, ping2_ret, ping2_time_ret, ping2_conf = check_sensors(cmd_queue)
        if ping2_ret != -100:
            ping2 = ping2_ret / 1000
        curr_depth = float(self.msg_handle.get_message(self.mavlink)['alt'])

        while time.time() <= end_time:
            ping1_ret, ping1_time_ret, ping1_conf, ping2_ret, ping2_time_ret, ping2_conf = check_sensors(cmd_queue)
            if ping2_ret != -100:
                ping2 = ping2_ret / 1000
            curr_depth = float(self.msg_handle.get_message(self.mavlink)['alt'])

            if ping2 != -100:
                if abs(ping2 - target_distance) > 0.2:
                    if ping2 > target_distance:
                        desired_depth = curr_depth - ping2 + target_distance
                    else:
                        desired_depth = curr_depth + (target_distance - ping2)

                    self.depth(throttle, desired_depth)
                    ping2 = -100
