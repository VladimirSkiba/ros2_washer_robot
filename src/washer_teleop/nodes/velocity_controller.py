#!/usr/bin/env python3
import argparse
import os
import yaml
import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node


class VelocityController(Node):
    def __init__(self, config_path):
        super().__init__('velocity_controller')
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        with open(config_path, encoding='utf-8') as stream:
            self.commands = yaml.safe_load(stream).get('commands', [])
        self.index = 0
        self.started_at = self.get_clock().now()
        self.timer = self.create_timer(0.05, self.tick)

    def tick(self):
        if self.index >= len(self.commands):
            self.publisher.publish(Twist())
            self.get_logger().info('Mission complete')
            self.timer.cancel()
            return
        command = self.commands[self.index]
        elapsed = (self.get_clock().now() - self.started_at).nanoseconds / 1e9
        if elapsed >= float(command['duration']):
            self.index += 1
            self.started_at = self.get_clock().now()
            return
        message = Twist()
        message.linear.x = float(command.get('linear', 0.0))
        message.angular.z = float(command.get('angular', 0.0))
        self.publisher.publish(message)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    args = parser.parse_args()
    rclpy.init()
    node = VelocityController(os.path.abspath(args.config))
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
