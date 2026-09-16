# ROS 2 Washer Robot

Симуляция робота-мойщика пола в Gazebo Harmonic. Роботом можно управлять с клавиатуры, а состояние и TF смотреть в RViz2.

## Важно: Docker

Dockerfile и Dev Container пока **не готовы к работе**. Запуск через Docker в текущем состоянии не поддерживается: контейнер не гарантирует корректное открытие окон Gazebo и RViz2.

Используйте установку ROS 2 непосредственно на Ubuntu-хосте. Инструкция ниже рассчитана на Ubuntu 24.04, ROS 2 Jazzy и Gazebo Harmonic.

## Состав проекта

- `washer_description` - URDF робота и конфигурация RViz2;
- `washer_gazebo` - мир Gazebo, спавн робота и `ros_gz_bridge`;
- `washer_teleop` - управление роботом клавишами `W`, `A`, `S`, `D`.

Пакета `washer_navigation` в текущем исходном дереве нет. Поэтому команды для SLAM, записи траектории и `full_simulation.launch.py` пока не являются рабочими и в эту инструкцию не включены.

## Установка на Ubuntu-хост

### 1. Установить ROS 2 Jazzy

Если ROS 2 Jazzy еще не установлен, следуйте официальной инструкции для Ubuntu 24.04:

<https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html>

После установки проверьте, что ROS доступен:

```bash
source /opt/ros/jazzy/setup.bash
ros2 --version
```

### 2. Установить зависимости проекта

```bash
sudo apt update
sudo apt install -y \
  ros-jazzy-ros-gz \
  ros-jazzy-rviz2 \
  ros-jazzy-robot-state-publisher \
  ros-jazzy-joint-state-publisher \
  ros-jazzy-xacro \
  python3-colcon-common-extensions
```

Gazebo Harmonic устанавливается вместе с пакетом `ros-jazzy-ros-gz`. Проверить его можно командой:

```bash
gz sim --version
```

### 3. Скачать проект и собрать workspace

```bash
cd ~
git clone https://github.com/VladimirSkiba/ros2_washer_robot.git я
cd ~/ros2_washer_robot

source /opt/ros/jazzy/setup.bash
rosdep update
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

Если проект уже скачан, достаточно перейти в его каталог и выполнить сборку:

```bash
cd ~/ros2_washer_robot
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash
```

После изменения `package.xml`, `CMakeLists.txt` или URDF повторяйте `colcon build --symlink-install`.

## Запуск проекта

Окна Gazebo и RViz2 могут не открываться из встроенного терминала VS Code. Для запуска используйте обычный терминал Ubuntu. Удобный вариант - Terminator:

```bash
sudo apt install terminator
```

### Горячие клавиши Terminator

| Сочетание | Действие |
|---|---|
| `Ctrl+Shift+O` | разделить окно по горизонтали |
| `Ctrl+Shift+E` | разделить окно по вертикали |
| `Alt+Стрелки` | переключиться между областями |

В каждом новом терминале сначала выполните:

```bash
cd ~/ros2_washer_robot
source /opt/ros/jazzy/setup.bash
source install/setup.bash
```

Можно использовать готовый скрипт:

```bash
cd ~/ros2_washer_robot
source env.sh
```

### Терминал 1: Gazebo

```bash
ros2 launch washer_gazebo sim.launch.py
```

Должно открыться окно Gazebo с помещением и роботом. Не закрывайте этот терминал во время работы.

### Терминал 2: RViz2

```bash
rviz2 -d ~/ros2_washer_robot/src/washer_description/rviz/lidar_vizion.rviz
```

Если RViz запущен без конфигурации, выберите `base_link` как `Fixed Frame` и добавьте `RobotModel` с источником `/robot_description`.

### Терминал 3: управление клавиатурой

```bash
ros2 run washer_teleop keyboard_control.py
```

Клавиши управления:

| Клавиша | Действие |
|---|---|
| `W` | движение вперед |
| `S` | движение назад |
| `A` | поворот влево |
| `D` | поворот вправо |
| `Space` или `K` | остановка |
| `Ctrl+C` | выход |

## Быстрая проверка

В отдельном терминале, после запуска Gazebo, можно проверить основные topics:

```bash
ros2 topic list
ros2 topic echo /odom --once
ros2 topic echo /scan --once
ros2 topic info /cmd_vel
```

Ожидаемые topics:

- `/cmd_vel` - команды скорости;
- `/odom` - одометрия робота;
- `/scan` - данные лидара;
- `/tf` и `/tf_static` - TF-дерево;
- `/robot_description` - URDF робота.

Для разовой проверки движения можно отправить команду вручную:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.3}, angular: {z: 0.0}}"
```

Остановить робота:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist '{}'
```

## Запуск только визуализации URDF

Если Gazebo не нужен, можно открыть модель робота в RViz2:

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 launch washer_description display.launch.py
```

Этот launch-файл запускает `robot_state_publisher`, `joint_state_publisher` и RViz2.


### Команда ROS 2 не найдена

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_washer_robot/install/setup.bash
```

### Пакет не найден после сборки

```bash
cd ~/ros2_washer_robot
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash
ros2 pkg list | grep washer
```

### Робот не двигается

Убедитесь, что Gazebo запущен, а `keyboard_control.py` работает в отдельном терминале. Затем проверьте:

```bash
ros2 topic echo /cmd_vel
ros2 topic info /cmd_vel
```

## Ограничения текущей версии

- Docker и Dev Container пока нерабочие и не используются в инструкции запуска.
- SLAM Toolbox, Nav2, сохранение карты и логирование траектории отсутствуют в текущем исходном дереве.
- Для работы GUI нужен локальный графический сеанс Ubuntu или корректно настроенный X11/Wayland.
- После пересборки необходимо заново выполнить `source install/setup.bash`.
