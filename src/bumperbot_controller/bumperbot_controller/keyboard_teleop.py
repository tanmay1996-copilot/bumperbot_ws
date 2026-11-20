#!/usr/bin/env python3

import select
import sys
import termios
import tty

import rclpy
from geometry_msgs.msg import TwistStamped
from rclpy.node import Node


class KeyboardTeleop(Node):
    def __init__(self):
        super().__init__("keyboard_teleop")
        self.declare_parameter("command_topic", "/bumperbot_keyboard/cmd_vel")
        command_topic = self.get_parameter("command_topic").value
        self.publisher = self.create_publisher(
            TwistStamped, command_topic, 10
        )
        self.timer = self.create_timer(0.1, self.publish_command)

        self.linear_speed = 0.0
        self.angular_speed = 0.0
        self.declare_parameter("max_linear_speed", 1.0)
        self.declare_parameter("max_angular_speed", 0.5)
        self.declare_parameter("speed_step", 0.05)
        self.max_linear_speed = self.get_parameter("max_linear_speed").value
        self.max_angular_speed = self.get_parameter("max_angular_speed").value
        self.speed_step = self.get_parameter("speed_step").value

    def handle_key(self, key):
        if key == "w":
            self.linear_speed = min(
                self.linear_speed + self.speed_step, self.max_linear_speed
            )
        elif key == "x":
            self.linear_speed = max(
                self.linear_speed - self.speed_step, -self.max_linear_speed
            )
        elif key == "a":
            self.angular_speed = min(
                self.angular_speed + self.speed_step, self.max_angular_speed
            )
        elif key == "d":
            self.angular_speed = max(
                self.angular_speed - self.speed_step, -self.max_angular_speed
            )
        elif key == "s":
            self.linear_speed = 0.0
            self.angular_speed = 0.0
        else:
            return False

        self.get_logger().info(
            f"linear: {self.linear_speed:.2f} m/s, "
            f"angular: {self.angular_speed:.2f} rad/s"
        )
        return True

    def publish_command(self):
        message = TwistStamped()
        message.header.stamp = self.get_clock().now().to_msg()
        message.twist.linear.x = self.linear_speed
        message.twist.angular.z = self.angular_speed
        self.publisher.publish(message)


def main(args=None):
    rclpy.init(args=args)
    node = KeyboardTeleop()
    input_stream = sys.stdin
    terminal = None

    if not input_stream.isatty():
        try:
            terminal = open("/dev/tty")
            input_stream = terminal
        except OSError as error:
            node.get_logger().error(
                "Keyboard teleop needs a terminal. Run it from an interactive shell. "
                f"Could not open /dev/tty: {error}"
            )
            node.destroy_node()
            rclpy.shutdown()
            return

    settings = termios.tcgetattr(input_stream)

    print("Keyboard teleop: w=forward, x=reverse, a=left, d=right, s=stop, q=quit")
    print("Each movement key changes speed by 0.05; max angular speed is 0.5 rad/s.")

    try:
        tty.setcbreak(input_stream.fileno())
        while rclpy.ok():
            readable, _, _ = select.select([input_stream], [], [], 0.1)
            if readable:
                key = input_stream.read(1).lower()
                if key == "q":
                    break
                node.handle_key(key)
            rclpy.spin_once(node, timeout_sec=0.0)
    except KeyboardInterrupt:
        pass
    finally:
        node.linear_speed = 0.0
        node.angular_speed = 0.0
        try:
            if rclpy.ok():
                node.publish_command()
        except Exception:
            pass
        finally:
            termios.tcsetattr(input_stream, termios.TCSADRAIN, settings)
            if terminal is not None:
                terminal.close()
            node.destroy_node()
            if rclpy.ok():
                rclpy.shutdown()


if __name__ == "__main__":
    main()
