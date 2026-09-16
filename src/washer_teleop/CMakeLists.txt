cmake_minimum_required(VERSION 3.8)
project(washer_teleop)

find_package(ament_cmake REQUIRED)
find_package(rclpy REQUIRED)
find_package(geometry_msgs REQUIRED)

install(PROGRAMS
  keyboard_control.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()