я хз почему но при запуске из терминала VScode окна GAZEBO и rviz не открываются 

по этому их стоит выполнять в обычном терминале 

для удобства лучше всего использовать терминал терминатор 

```
sudo apt install terminator
```

Ctrl + Shift + O — разделить окно по горизонтали.

Ctrl + Shift + E — разделить окно по вертикали.

Alt + Стрелки — переключение между областями терминала.

```
cd ros2_washer_robot/
```
### Подключить ROS2 и окружение 
```
source /opt/ros/jazzy/setup.bash

source install/setup.bash
```
### чтобы не парится и постоянно не вводить эти 2 команды я создал скрипт на bash привызове он сорсит эти 2 команды 
```
source env.sh
```
### или
```
. env.sh
```

```
ros2 launch washer_navigation full_simulation.launch.py mode:=keyboard
```

```
ros2 launch washer_navigation full_simulation.launch.py mode:=script
```


```
colcon build --packages-select washer_gazebo
```

```
source install/setup.bash
```

```
ros2 launch washer_gazebo sim.launch.py
```

### Управление с клавиатуры 
```
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```
### Как пользоваться:
* Нажми i — ехать вперед.

* Нажми , (запятая) — ехать назад.

* Нажми j — поворот влево.

* Нажми l — поворот вправо.

* Нажми k или пробел — стоп.

* Нажми q или z — увеличить/уменьшить скорость.

* Чтобы выйти, нажми Ctrl+C.


## Визуализация лидара в RViz2
```
rviz2
```

```
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```