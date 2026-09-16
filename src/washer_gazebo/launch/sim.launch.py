import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg_washer_description = get_package_share_directory('washer_description')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    
    # Просто читаем URDF файл
    urdf_file = os.path.join(pkg_washer_description, 'urdf', 'robot_compiled.urdf')
    with open(urdf_file, 'r') as f:
        robot_description = f.read()

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments=[
            ('gz_args', '-r /home/laptop/ros2_washer_robot/src/washer_gazebo/worlds/cleaning_environment.sdf')
        ]
    )

    rsp = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': True
        }]
    )

    # Мост между Gazebo и ROS 2
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model'
        ],
        output='screen'
    )

    spawn = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'washer_robot', '-z', '0.12'],
        output='screen'
    )

    return LaunchDescription([gz_sim, rsp, bridge, spawn])