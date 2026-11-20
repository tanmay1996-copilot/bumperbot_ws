#!/usr/bin/env python3

import time

import rclpy
from geometry_msgs.msg import TwistStamped
from rclpy.node import Node


class CmdVelPriorityMux(Node):
    def __init__(self):
        super().__init__("cmd_vel_priority_mux")
        self.declare_parameter("joystick_timeout", 0.5)
        self.declare_parameter("keyboard_timeout", 0.5)
        self.joystick_timeout = self.get_parameter("joystick_timeout").value
        self.keyboard_timeout = self.get_parameter("keyboard_timeout").value

        self.normal_command = TwistStamped()
        self.keyboard_command = TwistStamped()
        self.joystick_command = TwistStamped()
        self.last_normal_command = 0.0
        self.last_keyboard_command = 0.0
        self.last_joystick_command = 0.0

        self.publisher = self.create_publisher(
            TwistStamped, "/bumperbot_controller/cmd_vel", 10
        )
        self.create_subscription(
            TwistStamped,
            "/bumperbot_controller/input_cmd_vel",
            self.normal_callback,
            10,
        )
        self.create_subscription(
            TwistStamped,
            "/bumperbot_keyboard/cmd_vel",
            self.keyboard_callback,
            10,
        )
        self.create_subscription(
            TwistStamped,
            "/bumperbot_joystick/cmd_vel",
            self.joystick_callback,
            10,
        )
        self.timer = self.create_timer(0.1, self.publish_selected_command)

    def normal_callback(self, message):
        self.normal_command = message
        self.last_normal_command = time.monotonic()

    def keyboard_callback(self, message):
        self.keyboard_command = message
        self.last_keyboard_command = time.monotonic()

    def joystick_callback(self, message):
        self.joystick_command = message
        self.last_joystick_command = time.monotonic()

    def publish_selected_command(self):
        now = time.monotonic()
        if now - self.last_joystick_command < self.joystick_timeout:
            selected_command = self.joystick_command
        elif now - self.last_keyboard_command < self.keyboard_timeout:
            selected_command = self.keyboard_command
        else:
            selected_command = self.normal_command

        output = TwistStamped()
        output.header.stamp = self.get_clock().now().to_msg()
        output.twist = selected_command.twist
        self.publisher.publish(output)


def main(args=None):
    rclpy.init(args=args)
    node = CmdVelPriorityMux()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
