#!/bin/bash

# Подключаем базовый ROS 2 Jazzy
source /opt/ros/jazzy/setup.bash

if [ -f "install/setup.bash" ]; then
    source install/setup.bash
    echo "ROS 2 Jazzy и рабочее пространство успешно подключены!"
else
    echo "ROS 2 Jazzy подключен, но install/setup.bash не найден в текущей папке."
fi