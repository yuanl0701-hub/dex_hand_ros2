"""Launch a physical MPD20 hand from separated configuration layers."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterFile, ParameterValue


def generate_launch_description() -> LaunchDescription:
    share = get_package_share_directory("dex_hand_ros2")
    default_runtime = os.path.join(share, "config", "runtime", "default.yaml")
    default_physical_runtime = os.path.join(
        share, "config", "runtime", "physical_conservative.yaml"
    )
    default_backend = os.path.join(share, "config", "backends", "mpd20.yaml")
    default_model = os.path.join(
        share, "config", "hand_models", "mpd20_six_axis", "ros_parameters.yaml"
    )
    default_deployment = os.path.join(
        share, "config", "deployments", "mpd20_hand.example.yaml"
    )
    default_gestures = os.path.join(
        share,
        "config",
        "hand_models",
        "mpd20_six_axis",
        "commissioning_gestures.json",
    )
    return LaunchDescription(
        [
            DeclareLaunchArgument("runtime_config", default_value=default_runtime),
            DeclareLaunchArgument(
                "physical_runtime_config", default_value=default_physical_runtime
            ),
            DeclareLaunchArgument("backend_config", default_value=default_backend),
            DeclareLaunchArgument("hand_model_config", default_value=default_model),
            # Historical alias retained for callers that used config_file.
            DeclareLaunchArgument("config_file", default_value=default_deployment),
            DeclareLaunchArgument(
                "deployment_config", default_value=LaunchConfiguration("config_file")
            ),
            DeclareLaunchArgument("gesture_file", default_value=default_gestures),
            DeclareLaunchArgument("serial_port", default_value="/dev/ttyUSB0"),
            DeclareLaunchArgument("baudrate", default_value="115200"),
            DeclareLaunchArgument("motion_enabled", default_value="false"),
            Node(
                package="dex_hand_ros2",
                executable="hand_node",
                name="dex_hand_node",
                output="screen",
                emulate_tty=True,
                parameters=[
                    ParameterFile(LaunchConfiguration("runtime_config"), allow_substs=True),
                    ParameterFile(
                        LaunchConfiguration("physical_runtime_config"), allow_substs=True
                    ),
                    ParameterFile(LaunchConfiguration("backend_config"), allow_substs=True),
                    ParameterFile(LaunchConfiguration("hand_model_config"), allow_substs=True),
                    ParameterFile(LaunchConfiguration("deployment_config"), allow_substs=True),
                    {
                        "serial_port": LaunchConfiguration("serial_port"),
                        "baudrate": ParameterValue(
                            LaunchConfiguration("baudrate"), value_type=int
                        ),
                        "hardware_motion_enabled": ParameterValue(
                            LaunchConfiguration("motion_enabled"), value_type=bool
                        ),
                        "gesture_file": LaunchConfiguration("gesture_file"),
                    },
                ],
            ),
        ]
    )
