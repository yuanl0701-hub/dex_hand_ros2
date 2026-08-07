"""Run the simulated controller as a position-command source for Isaac Sim."""

from __future__ import annotations

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterFile, ParameterValue


def generate_launch_description() -> LaunchDescription:
    share = get_package_share_directory("dex_hand_ros2")
    runtime = os.path.join(share, "config", "runtime", "default.yaml")
    simulation_runtime = os.path.join(share, "config", "runtime", "simulation.yaml")
    backend = os.path.join(share, "config", "backends", "simulated.yaml")
    default_model = os.path.join(
        share, "config", "hand_models", "revo2_right", "ros_parameters.yaml"
    )
    gestures = os.path.join(
        share, "config", "hand_models", "generic_six_axis", "gestures.json"
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("runtime_config", default_value=runtime),
            DeclareLaunchArgument("simulation_runtime_config", default_value=simulation_runtime),
            DeclareLaunchArgument("backend_config", default_value=backend),
            # config_file is retained as an alias for the historical script.
            DeclareLaunchArgument("config_file", default_value=default_model),
            DeclareLaunchArgument(
                "hand_model_config", default_value=LaunchConfiguration("config_file")
            ),
            DeclareLaunchArgument("gesture_file", default_value=gestures),
            DeclareLaunchArgument(
                "joint_command_topic", default_value="/dex_hand/joint_command"
            ),
            DeclareLaunchArgument("simulation_update_rate", default_value="100.0"),
            DeclareLaunchArgument("qos_reliability", default_value="reliable"),
            Node(
                package="dex_hand_ros2",
                executable="hand_node",
                name="dex_hand_node",
                output="screen",
                parameters=[
                    ParameterFile(LaunchConfiguration("runtime_config"), allow_substs=True),
                    ParameterFile(
                        LaunchConfiguration("simulation_runtime_config"), allow_substs=True
                    ),
                    ParameterFile(LaunchConfiguration("backend_config"), allow_substs=True),
                    ParameterFile(LaunchConfiguration("hand_model_config"), allow_substs=True),
                    {
                        "gesture_file": LaunchConfiguration("gesture_file"),
                        "joint_command_topic": LaunchConfiguration("joint_command_topic"),
                        "simulation_update_rate": ParameterValue(
                            LaunchConfiguration("simulation_update_rate"), value_type=float
                        ),
                        "qos_reliability": LaunchConfiguration("qos_reliability"),
                    },
                ],
            ),
        ]
    )
