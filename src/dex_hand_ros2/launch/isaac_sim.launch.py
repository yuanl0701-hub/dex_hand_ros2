"""Run the hand controller as a position-command source for Isaac Sim."""

from __future__ import annotations

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description() -> LaunchDescription:
    share = get_package_share_directory("dex_hand_ros2")
    config = os.path.join(share, "config", "isaac_sim.yaml")
    gesture_file = os.path.join(share, "config", "gestures.yaml")

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "joint_command_topic",
                default_value="/dex_hand/joint_command",
            ),
            DeclareLaunchArgument(
                "simulation_update_rate",
                default_value="100.0",
            ),
            DeclareLaunchArgument(
                "qos_reliability",
                default_value="reliable",
            ),
            Node(
                package="dex_hand_ros2",
                executable="hand_node",
                name="dex_hand_node",
                output="screen",
                parameters=[
                    config,
                    {
                        "gesture_file": gesture_file,
                        "joint_command_topic": LaunchConfiguration(
                            "joint_command_topic"
                        ),
                        "simulation_update_rate": ParameterValue(
                            LaunchConfiguration("simulation_update_rate"),
                            value_type=float,
                        ),
                        "qos_reliability": LaunchConfiguration(
                            "qos_reliability"
                        ),
                    },
                ],
            ),
        ]
    )
