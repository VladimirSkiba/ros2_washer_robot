from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    name = LaunchConfiguration('name')
    return LaunchDescription([
        DeclareLaunchArgument('name', default_value='maps/my_map'),
        ExecuteProcess(cmd=['ros2', 'service', 'call', '/slam_toolbox/save_map', 'slam_toolbox/srv/SaveMap', '{name: {data: ', name, '}}'], output='screen'),
    ])
