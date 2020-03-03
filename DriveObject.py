import time
import numpy as np
class DriveObject:
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

    def drive_straight(self, throttle, direction):
        # direction:
        #  1: forward
        # -1: backward
        output = (direction * throttle * 5) + 1500
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

    def turn(self, throttle, angle, current_header, original_header):
        # -1: Port
        #  1: Starboard
        direction = np.sign(angle)
        output = (direction*throttle * 5) + 1500

        self.write_pwm(3, output)

    # to certain distance
    def depth(self, throttle, target_depth):
        if 0 < throttle <= 100:
            curr_depth = float(self.msg_handle.get_message(self.mavlink)['alt'])
            output = (throttle * 5) + 1500
            if (target_depth - curr_depth) < 0:
                output = (-throttle * 5) + 1500

            while abs(target_depth - curr_depth) > 0.2:
                self.write_pwm( 2, output)
                curr_depth = float(self.msg_handle.get_message(self.mavlink)['alt'])
        elif throttle == 0:
            self.write_pwm(2, 0)

    #hold at 1m off bottom
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

    def check_sensors(q):
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