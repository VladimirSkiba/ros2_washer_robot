#!/usr/bin/env python3
import csv
import math
import os
from datetime import datetime
import rclpy
from nav_msgs.msg import Odometry
from rclpy.node import Node


class TrajectoryLogger(Node):
    def __init__(self):
        super().__init__('trajectory_logger')
        root = os.environ.get('ROS2_WASHER_ROOT', os.path.expanduser('~/ros2_washer_robot'))
        log_dir = os.path.join(root, 'src', 'washer_navigation', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        path = os.path.join(log_dir, f'trajectory_{datetime.now():%Y-%m-%d_%H-%M-%S}.csv')
        self.file = open(path, 'w', newline='', encoding='utf-8')
        self.writer = csv.writer(self.file)
        self.writer.writerow(['timestamp', 'x', 'y', 'yaw', 'linear_velocity', 'angular_velocity'])
        self.subscription = self.create_subscription(Odometry, '/odom', self.on_odom, 20)
        self.get_logger().info(f'Logging trajectory to {path}')

    def on_odom(self, message):
        q = message.pose.pose.orientation
        yaw = math.atan2(2.0 * (q.w * q.z + q.x * q.y), 1.0 - 2.0 * (q.y * q.y + q.z * q.z))
        stamp = message.header.stamp.sec + message.header.stamp.nanosec / 1e9
        self.writer.writerow([f'{stamp:.6f}', f'{message.pose.pose.position.x:.4f}', f'{message.pose.pose.position.y:.4f}', f'{yaw:.4f}', f'{message.twist.twist.linear.x:.4f}', f'{message.twist.twist.angular.z:.4f}'])
        self.file.flush()

    def destroy_node(self):
        self.file.close()
        super().destroy_node()


def main():
    rclpy.init()
    node = TrajectoryLogger()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
