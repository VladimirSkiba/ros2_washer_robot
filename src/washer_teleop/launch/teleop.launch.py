import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node


def generate_launch_description():
    mode = LaunchConfiguration('mode')
    config = os.path.join(get_package_share_directory('washer_teleop'), 'config', 'mission.yaml')
    return LaunchDescription([
        DeclareLaunchArgument('mode', default_value='keyboard', choices=['keyboard', 'script']),
        Node(package='teleop_twist_keyboard', executable='teleop_twist_keyboard', output='screen',
             prefix='xterm -e', condition=IfCondition(PythonExpression(["'", mode, "' == 'keyboard'"]))),
        Node(package='washer_teleop', executable='velocity_controller.py', output='screen',
             arguments=['--config', config], condition=UnlessCondition(PythonExpression(["'", mode, "' == 'keyboard'"]))),
    ])
