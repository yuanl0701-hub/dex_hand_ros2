"""Launch the simulated backend with a separately selected hand model."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterFile, ParameterValue


def generate_launch_description() -> LaunchDescription:
    share = get_package_share_directory("dex_hand_ros2")
    model = os.path.join(share, "urdf", "virtual_dex_hand.urdf.xacro")
    runtime = os.path.join(share, "config", "runtime", "default.yaml")
    simulation_runtime = os.path.join(share, "config", "runtime", "simulation.yaml")
    backend = os.path.join(share, "config", "backends", "simulated.yaml")
    hand_model = os.path.join(
        share, "config", "hand_models", "generic_six_axis", "ros_parameters.yaml"
    )
    gestures = os.path.join(
        share, "config", "hand_models", "generic_six_axis", "gestures.json"
    )
    rviz_config = os.path.join(share, "rviz", "virtual_dex_hand.rviz")
    robot_description = ParameterValue(Command(["xacro ", model]), value_type=str)
    return LaunchDescription(
        [
            DeclareLaunchArgument("use_rviz", default_value="true"),
            DeclareLaunchArgument("runtime_config", default_value=runtime),
            DeclareLaunchArgument("simulation_runtime_config", default_value=simulation_runtime),
            DeclareLaunchArgument("backend_config", default_value=backend),
            DeclareLaunchArgument("hand_model_config", default_value=hand_model),
            DeclareLaunchArgument("gesture_file", default_value=gestures),
            DeclareLaunchArgument("simulation_update_rate", default_value="100.0"),
            DeclareLaunchArgument("deterministic_mode", default_value="true"),
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
                        "simulation_update_rate": ParameterValue(
                            LaunchConfiguration("simulation_update_rate"), value_type=float
                        ),
                        "sim_deterministic_mode": ParameterValue(
                            LaunchConfiguration("deterministic_mode"), value_type=bool
                        ),
                    },
                ],
            ),
            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                name="robot_state_publisher",
                output="screen",
                parameters=[{"robot_description": robot_description}],
            ),
            Node(
                package="rviz2",
                executable="rviz2",
                name="rviz2",
                arguments=["-d", rviz_config],
                condition=IfCondition(LaunchConfiguration("use_rviz")),
                output="screen",
            ),
        ]
    )
