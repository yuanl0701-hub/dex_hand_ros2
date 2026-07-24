"""Launch the hand node with mock-safe defaults."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description() -> LaunchDescription:
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
                    }
                ],
            ),
        ]
    )
