import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg_washer_gazebo = get_package_share_directory('washer_gazebo')
    pkg_slam_toolbox = get_package_share_directory('slam_toolbox')
    
    # Параметры SLAM
    slam_params = {
        'use_sim_time': True,
        'odom_frame': 'odom',
        'map_frame': 'map',
        'base_frame': 'base_footprint',
        'scan_topic': '/scan',
        'mode': 'mapping',  # Режим построения карты
        'resolution': 0.05,  # Разрешение карты 5 см/пиксель
        'max_laser_range': 12.0,
        'minimum_time_interval': 0.5,
        'transform_publish_period': 0.05,
    }
    
    # Запуск SLAM Toolbox
    slam = Node(
        package='slam_toolbox',
        executable='sync_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[slam_params]
    )

    # Публикация TF от одометрии
    odom_tf = Node(
        package='washer_gazebo',
        executable='odom_tf_publisher.py',
        name='odom_tf_publisher',
        output='screen'
    )
    
    return LaunchDescription([odom_tf, slam])
    