
FROM ros:jazzy-ros-base

ENV DEBIAN_FRONTEND=noninteractive
ENV ROS_DISTRO=jazzy

# Установка ROS 2, Gazebo и инструментов разработки
RUN apt-get update && apt-get install -y \
    ros-jazzy-ros-gz \
    ros-jazzy-rviz2 \
    ros-jazzy-robot-state-publisher \
    ros-jazzy-joint-state-publisher \
    ros-jazzy-joint-state-publisher-gui \
    ros-jazzy-xacro \
    ros-jazzy-tf2-tools \
    ros-jazzy-ros2-control \
    ros-jazzy-ros2-controllers \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-pip \
    python3-numpy \
    git \
    nano \
    vim \
    x11-apps \
    mesa-utils \
    libgl1-mesa-dri \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория ROS-проекта
WORKDIR /workspace

# Автоматическая настройка ROS 2 для Bash
RUN echo "source /opt/ros/jazzy/setup.bash" >> /root/.bashrc

# Настройки для графических приложений
ENV QT_X11_NO_MITSHM=1
ENV LIBGL_ALWAYS_SOFTWARE=0

CMD ["bash"]