"""Launch the actuator-level plant and nominal virtual hand visualization."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description() -> LaunchDescription:
    share = get_package_share_directory("dex_hand_ros2")
    model = os.path.join(share, "urdf", "virtual_dex_hand.urdf.xacro")
    config = os.path.join(share, "config", "simulated_hand.yaml")
    gesture_file = os.path.join(share, "config", "gestures.yaml")
    rviz_config = os.path.join(share, "rviz", "virtual_dex_hand.rviz")
    robot_description = ParameterValue(Command(["xacro ", model]), value_type=str)
    use_rviz = LaunchConfiguration("use_rviz")
    update_rate = LaunchConfiguration("simulation_update_rate")
    deterministic = LaunchConfiguration("deterministic_mode")
    return LaunchDescription(
        [
            DeclareLaunchArgument("use_rviz", default_value="true"),
            DeclareLaunchArgument("simulation_update_rate", default_value="100.0"),
            DeclareLaunchArgument("deterministic_mode", default_value="true"),
            Node(
                package="dex_hand_ros2",
                executable="hand_node",
                name="dex_hand_node",
                output="screen",
                parameters=[
                    config,
                    {
                        "driver_type": "simulated",
                        "gesture_file": gesture_file,
                        "simulation_update_rate": ParameterValue(update_rate, value_type=float),
                        "sim_deterministic_mode": ParameterValue(deterministic, value_type=bool),
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
                condition=IfCondition(use_rviz),
                output="screen",
            ),
        ]
    )
