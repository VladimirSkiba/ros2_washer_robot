import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def include(package, launch_file, arguments=None):
    source = os.path.join(get_package_share_directory(package), 'launch', launch_file)
    return IncludeLaunchDescription(PythonLaunchDescriptionSource(source), launch_arguments=(arguments or {}).items())


def generate_launch_description():
    mode = LaunchConfiguration('mode')
    nav_share = get_package_share_directory('washer_navigation')
    return LaunchDescription([
        DeclareLaunchArgument('mode', default_value='keyboard', choices=['keyboard', 'script']),
        include('washer_gazebo', 'sim.launch.py'),
        include('washer_navigation', 'slam.launch.py'),
        include('washer_teleop', 'teleop.launch.py', {'mode': mode}),
        Node(package='washer_navigation', executable='trajectory_logger.py', output='screen'),
        Node(package='rviz2', executable='rviz2', output='screen', arguments=['-d', os.path.join(nav_share, 'rviz', 'slam.rviz')]),
    ])
