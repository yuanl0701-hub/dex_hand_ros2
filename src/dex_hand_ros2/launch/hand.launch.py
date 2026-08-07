"""Launch the generic ROS facade with independently selectable layers."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterFile


def generate_launch_description() -> LaunchDescription:
    share = get_package_share_directory("dex_hand_ros2")
    default_runtime = os.path.join(share, "config", "runtime", "default.yaml")
    default_backend = os.path.join(share, "config", "backends", "mock.yaml")
    default_model = os.path.join(
        share, "config", "hand_models", "generic_six_axis", "ros_parameters.yaml"
    )
    default_gestures = os.path.join(
        share, "config", "hand_models", "generic_six_axis", "gestures.json"
    )
    return LaunchDescription(
        [
            DeclareLaunchArgument("runtime_config", default_value=default_runtime),
            DeclareLaunchArgument("backend_config", default_value=default_backend),
            DeclareLaunchArgument("hand_model_config", default_value=default_model),
            DeclareLaunchArgument("gesture_file", default_value=default_gestures),
            Node(
                package="dex_hand_ros2",
                executable="hand_node",
                name="dex_hand_node",
                output="screen",
                parameters=[
                    ParameterFile(LaunchConfiguration("runtime_config"), allow_substs=True),
                    ParameterFile(LaunchConfiguration("backend_config"), allow_substs=True),
                    ParameterFile(LaunchConfiguration("hand_model_config"), allow_substs=True),
                    {"gesture_file": LaunchConfiguration("gesture_file")},
                ],
            ),
        ]
    )
