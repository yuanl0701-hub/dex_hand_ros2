"""Launch the hand node with mock-safe defaults."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description() -> LaunchDescription:
    share = get_package_share_directory("dex_hand_ros2")
    gesture_file = os.path.join(share, "config", "gestures.yaml")
    return LaunchDescription(
        [
            DeclareLaunchArgument("driver_type", default_value="fake"),
            DeclareLaunchArgument("serial_port", default_value="/dev/ttyUSB0"),
            DeclareLaunchArgument("qos_reliability", default_value="reliable"),
            DeclareLaunchArgument("qos_depth", default_value="10"),
            Node(
                package="dex_hand_ros2",
                executable="hand_node",
                name="dex_hand_node",
                output="screen",
                parameters=[
                    {
                        "driver_type": LaunchConfiguration("driver_type"),
                        "serial_port": LaunchConfiguration("serial_port"),
                        "qos_reliability": LaunchConfiguration("qos_reliability"),
                        "qos_depth": ParameterValue(
                            LaunchConfiguration("qos_depth"), value_type=int
                        ),
                        "gesture_file": gesture_file,
                    }
                ],
            ),
        ]
    )
