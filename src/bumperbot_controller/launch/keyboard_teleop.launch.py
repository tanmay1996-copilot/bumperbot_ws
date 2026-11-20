from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from launch.substitutions import LaunchConfiguration
import os

def generate_launch_description():
    command_topic_arg = DeclareLaunchArgument(
        "command_topic",
        default_value="/bumperbot_keyboard/cmd_vel",
        description="Velocity command topic used by keyboard teleop",
    )
    command_topic = LaunchConfiguration("command_topic")

    parameters_file = os.path.join(
        get_package_share_directory("bumperbot_controller"),
        "config",
        "keyboard_teleop.yaml",
    )

    keyboard_teleop = Node(
        package="bumperbot_controller",
        executable="keyboard_teleop.py",
        output="screen",
        emulate_tty=True,
        parameters=[parameters_file, {"command_topic": command_topic}],
    )

    return LaunchDescription([command_topic_arg, keyboard_teleop])