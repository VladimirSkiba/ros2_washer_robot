import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    gazebo_share = get_package_share_directory('washer_gazebo')
    description_share = get_package_share_directory('washer_description')
    world = os.path.join(gazebo_share, 'worlds', 'cleaning_environment.sdf')
    urdf = os.path.join(description_share, 'urdf', 'robot.urdf')

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': ['-r ', world]}.items(),
    )
    robot_description = Command(['cat ', urdf])
    rsp = Node(package='robot_state_publisher', executable='robot_state_publisher',
               parameters=[{'robot_description': robot_description, 'use_sim_time': True}])
    jsp = Node(package='joint_state_publisher', executable='joint_state_publisher',
               parameters=[{'use_sim_time': True}])
    spawn = Node(package='ros_gz_sim', executable='create', output='screen',
                 arguments=['-name', 'washer_robot', '-topic', 'robot_description',
                            '-x', '0', '-y', '0', '-z', '0.50'])
    bridge = Node(package='ros_gz_bridge', executable='parameter_bridge', output='screen',
                  arguments=[
                      '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
                      '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
                      '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
                      '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
                  ], parameters=[{'use_sim_time': True}])
    return LaunchDescription([gz_sim, rsp, jsp, spawn, bridge])
