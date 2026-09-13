FROM osrf/ros:jazzy-desktop-full
SHELL ["/bin/bash", "-c"]

RUN apt-get update && apt-get install -y --no-install-recommends \
    ros-jazzy-ros-gz \
    ros-jazzy-slam-toolbox \
    ros-jazzy-navigation2 \
    ros-jazzy-nav2-bringup \
    ros-jazzy-teleop-twist-keyboard \
    python3-yaml \
    xterm \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /home/ros2_washer_robot
COPY . /home/ros2_washer_robot
RUN source /opt/ros/jazzy/setup.bash && colcon build --symlink-install

RUN echo 'source /opt/ros/jazzy/setup.bash' >> /root/.bashrc && \
    echo 'source /home/ros2_washer_robot/install/setup.bash' >> /root/.bashrc
CMD ["bash"]
