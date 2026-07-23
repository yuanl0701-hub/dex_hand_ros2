"""Launch the hand node with mock-safe defaults."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            DeclareLaunchArgument("driver_type", default_value="fake"),
            DeclareLaunchArgument("serial_port", default_value="/dev/ttyUSB0"),
            Node(
                package="dex_hand_ros2",
                executable="hand_node",
                name="dex_hand_node",
                output="screen",
                parameters=[
                    {
                        "driver_type": LaunchConfiguration("driver_type"),
                        "serial_port": LaunchConfiguration("serial_port"),
                    }
                ],
            ),
        ]
    )
