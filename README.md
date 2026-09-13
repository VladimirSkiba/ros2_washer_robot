# ROS 2 Jazzy Washer Robot

Симуляция робота-мойщика пола в Gazebo Harmonic с управлением от клавиатуры или по сценарию, лидаром, одометрией, SLAM Toolbox, RViz2 и записью траектории в CSV.

Проект рассчитан на **Ubuntu 24.04**, **ROS 2 Jazzy** и **Gazebo Harmonic**. На Windows запуск выполняется через Docker Desktop и VS Code Dev Containers.

## 1. Что делает система

После запуска система:

1. Запускает Gazebo с помещением 20 x 10 м, стенами, столами, колоннами и перегородками.
2. Загружает URDF робота и размещает его в точке `(0, 0, 0.50)`, чтобы колёса не пересекались с полом при старте.
3. Публикует команды движения в `/cmd_vel`.
4. Получает из Gazebo одометрию `/odom` и лазерные измерения `/scan` через `ros_gz_bridge`.
5. Запускает SLAM Toolbox, который строит карту `/map` и публикует TF `map -> odom`.
6. Показывает робота, лидар, карту, TF и траекторию в RViz2.
7. Записывает данные одометрии в CSV-файл.

Основной интеграционный запуск:

```bash
ros2 launch washer_navigation full_simulation.launch.py mode:=keyboard
```

## 2. Архитектура данных

```text
teleop_twist_keyboard --+
                       +-- /cmd_vel --> Gazebo DiffDrive
velocity_controller ---+                    |
                                            +-- /odom --> trajectory_logger
                                            +-- /odom --> slam_toolbox
                                            +-- /scan --> slam_toolbox

Gazebo clock --> ros_gz_bridge --> /clock

slam_toolbox: /scan + TF odom/base_link --> /map + map->odom

robot_state_publisher: /robot_description --> TF base_link->laser_frame/wheels

RViz2: /robot_description, /scan, /map, /tf, /slam_toolbox/trajectory
```

### TF-дерево

```text
map
 └── odom                 (slam_toolbox)
      └── base_link       (Gazebo DiffDrive / odometry)
           ├── laser_frame
           ├── rear_left_wheel
           ├── rear_right_wheel
           └── caster_wheel
```

## 3. Структура проекта

```text
ros2_washer_robot/
├── .devcontainer/
│   └── devcontainer.json
├── .vscode/
│   ├── c_cpp_properties.json
│   └── settings.json
├── Dockerfile
├── README.md
├── .gitignore
└── src/
    ├── washer_description/
    ├── washer_gazebo/
    ├── washer_teleop/
    └── washer_navigation/
```

Каталоги `build/`, `install/` и `log/` создаются `colcon`. Они не являются исходным кодом и исключены из Git.

## 4. Пакет `washer_description`

Пакет содержит геометрию робота, frame-имена и Gazebo-плагины.

### `src/washer_description/urdf/robot.urdf`

Главное описание робота в формате URDF.

Внутри определены:

- `base_link` - корпус размером примерно `0.75 x 0.55 x 0.30` м и массой 18 кг;
- `laser_frame` - frame лидара над передней частью корпуса;
- `rear_left_wheel` и `rear_right_wheel` - ведущие колёса;
- `caster_wheel` - переднее опорное колесо;
- фиксированные и вращательные joints между корпусом и деталями;
- визуальные материалы синего корпуса, чёрных колёс и серебристого лидара.

В URDF также находятся Gazebo-элементы:

- `gz-sim-diff-drive-system` преобразует `/cmd_vel` в движение колёс и публикует `/odom`;
- `gpu_lidar` публикует лазерные измерения в `/scan`;
- frame одометрии - `odom`;
- дочерний frame робота - `base_link`.

Параметры лидара: 720 лучей, диапазон углов от `-pi` до `pi`, дальность от `0.12` до `12` м, частота 10 Гц.

### `src/washer_description/package.xml`

Описывает ROS 2-пакет и runtime-зависимости для `robot_state_publisher`, `joint_state_publisher` и Gazebo.

### `src/washer_description/CMakeLists.txt`

Минимальная конфигурация `ament_cmake`. Устанавливает каталог `urdf` в share-каталог пакета, чтобы launch-файлы могли найти `robot.urdf` через `ament_index`.

## 5. Пакет `washer_gazebo`

Пакет отвечает за мир Gazebo, запуск симулятора и bridge между Gazebo Transport и ROS 2.

### `src/washer_gazebo/worlds/cleaning_environment.sdf`

Основной authored-мир в формате SDF.

Содержит:

- пол размером 20 x 10 м;
- четыре стены высотой 2.5 м и толщиной 0.2 м;
- дневное направленное освещение и ambient-свет;
- серый пол;
- три стола;
- две цилиндрические колонны радиусом 0.3 м и высотой 2.5 м;
- две перегородки размером 2 x 0.1 x 1.5 м.

### `src/washer_gazebo/worlds/cleaning_environment.world`

Альтернативный SDF-файл с расширением `.world`. Он содержит совместимый standalone-мир и может использоваться для ручного запуска Gazebo. Текущий `sim.launch.py` использует полный `cleaning_environment.sdf`, чтобы все препятствия были загружены из одного файла.

### `src/washer_gazebo/launch/sim.launch.py`

Запускает отдельную симуляцию:

1. Подключает `ros_gz_sim/launch/gz_sim.launch.py`.
2. Загружает `cleaning_environment.sdf` в режиме запуска с работающей физикой.
3. Загружает URDF через `robot_state_publisher`.
4. Запускает `joint_state_publisher`.
5. Создаёт робота через `ros_gz_sim create` в точке `(0, 0, 0.50)`.
6. Запускает `ros_gz_bridge` для `/clock`, `/cmd_vel`, `/odom` и `/scan`.

### `src/washer_gazebo/package.xml`

Объявляет зависимости на `washer_description`, `ros_gz_sim`, `robot_state_publisher` и `joint_state_publisher`.

### `src/washer_gazebo/CMakeLists.txt`

Устанавливает каталоги `worlds` и `launch` в share-каталог пакета.

## 6. Пакет `washer_teleop`

Пакет предоставляет два способа управления роботом.

### `src/washer_teleop/launch/teleop.launch.py`

Принимает аргумент:

```text
mode:=keyboard
mode:=script
```

В режиме `keyboard` запускается стандартный пакет `teleop_twist_keyboard`. В launch-файле используется `xterm -e`, поэтому ему нужен графический терминал.

В режиме `script` запускается `velocity_controller.py`, которому передаётся установленный файл `config/mission.yaml`.

### `src/washer_teleop/nodes/velocity_controller.py`

Python-узел ROS 2, который:

1. Читает путь к YAML через обязательный аргумент `--config`.
2. Загружает список `commands`.
3. Каждые 50 мс публикует `geometry_msgs/msg/Twist` в `/cmd_vel`.
4. Использует `linear` как `Twist.linear.x`.
5. Использует `angular` как `Twist.angular.z`.
6. После истечения `duration` переходит к следующей команде.
7. После завершения миссии публикует нулевой `Twist` и останавливает timer.

Обычно вручную запускать его не требуется: это делает `teleop.launch.py`.

### `src/washer_teleop/config/mission.yaml`

Сценарий движения. Каждая команда имеет вид:

```yaml
commands:
  - linear: 0.3
    angular: 0.0
    duration: 15.0
```

Значения скоростей задаются в метрах в секунду и радианах в секунду. Время задаётся в секундах. Для новой миссии измените этот файл и перезапустите сценарий.

### `src/washer_teleop/package.xml` и `CMakeLists.txt`

`package.xml` объявляет `rclpy`, `geometry_msgs`, `teleop_twist_keyboard` и `python3-yaml`.

`CMakeLists.txt` устанавливает launch/config и регистрирует `velocity_controller.py` как исполняемый ROS 2-узел.

## 7. Пакет `washer_navigation`

Пакет содержит SLAM, RViz, сохранение карты и запись траектории.

### `src/washer_navigation/launch/slam.launch.py`

Запускает `slam_toolbox` с executable `async_slam_toolbox_node` и параметрами из `config/slam_params.yaml`.

### `src/washer_navigation/config/slam_params.yaml`

Основные параметры SLAM:

| Параметр | Значение | Назначение |
|---|---|---|
| `use_sim_time` | `true` | Использовать clock Gazebo |
| `odom_frame` | `odom` | Frame одометрии |
| `map_frame` | `map` | Frame карты |
| `base_frame` | `base_link` | Frame робота |
| `scan_topic` | `/scan` | Источник лидара |
| `publish_tf` | `true` | Публиковать `map -> odom` |
| `resolution` | `0.05` | Разрешение карты в метрах |
| `mode` | `mapping` | Режим построения карты |
| `map_update_interval` | `2.0` | Период обновления карты |
| `max_laser_range` | `12.0` | Максимальная дальность лидара |

### `src/washer_navigation/launch/save_map.launch.py`

Объявляет аргумент `name` и вызывает сервис `/slam_toolbox/save_map` типа `slam_toolbox/srv/SaveMap`.

Пример:

```bash
ros2 launch washer_navigation save_map.launch.py \
  name:=/home/ros2_washer_robot/src/washer_navigation/maps/my_map
```

Также можно вызвать сервис напрямую:

```bash
ros2 service call /slam_toolbox/save_map slam_toolbox/srv/SaveMap \
  "{name: {data: '/home/ros2_washer_robot/src/washer_navigation/maps/my_map'}}"
```

SLAM Toolbox обычно создаёт файлы карты с расширениями `.yaml` и `.pgm`.

### `src/washer_navigation/nodes/trajectory_logger.py`

Узел подписывается на `/odom` типа `nav_msgs/msg/Odometry`.

При каждом сообщении он записывает:

```text
timestamp,x,y,yaw,linear_velocity,angular_velocity
```

`yaw` вычисляется из quaternion-ориентации робота. CSV создаётся в:

```text
src/washer_navigation/logs/trajectory_YYYY-MM-DD_HH-MM-SS.csv
```

Корень workspace берётся из переменной `ROS2_WASHER_ROOT`. Если она не задана, используется `~/ros2_washer_robot`.

### `src/washer_navigation/rviz/slam.rviz`

Готовая конфигурация RViz2:

- Fixed Frame: `map`;
- RobotModel из `/robot_description`;
- LaserScan из `/scan`, зелёные точки размером 0.05 м;
- Map из `/map` с цветовой схемой `map`;
- TF со всеми frame и именами;
- Path из `/slam_toolbox/trajectory`;
- TopDownOrtho-вид сверху.

### `src/washer_navigation/launch/full_simulation.launch.py`

Единый launch-файл, который включает:

1. `washer_gazebo/sim.launch.py`;
2. `washer_navigation/slam.launch.py`;
3. `washer_teleop/teleop.launch.py` с переданным `mode`;
4. `trajectory_logger.py`;
5. RViz2 с `rviz/slam.rviz`.

### `src/washer_navigation/package.xml` и `CMakeLists.txt`

`package.xml` объявляет зависимости на `rclpy`, `nav_msgs`, `slam_toolbox`, `rviz2`, `washer_gazebo` и `washer_teleop`.

`CMakeLists.txt` устанавливает launch/config/rviz/maps и регистрирует `trajectory_logger.py` как исполняемый ROS 2-узел.

### `src/washer_navigation/maps/.gitkeep`

Пустой marker-файл, сохраняющий каталог `maps` в Git. Сгенерированные карты обычно исключены из Git через `.gitignore`.

## 8. Docker и Dev Container

### `Dockerfile`

Основой служит `osrf/ros:jazzy-desktop-full`.

Во время сборки Docker устанавливает `ros-jazzy-ros-gz`, `ros-jazzy-slam-toolbox`, `ros-jazzy-navigation2`, `ros-jazzy-nav2-bringup`, `ros-jazzy-teleop-twist-keyboard`, `python3-yaml` и `xterm`.

Затем исходники копируются в `/home/ros2_washer_robot`, выполняется `colcon build --symlink-install`, а ROS и workspace добавляются в `/root/.bashrc`.

### `.devcontainer/devcontainer.json`

Конфигурация VS Code Dev Containers:

- собирает контейнер из `../Dockerfile`;
- открывает workspace как `/home/ros2_washer_robot`;
- монтирует локальную папку проекта внутрь контейнера;
- устанавливает расширения ROS, Python и Pylance;
- задаёт `ROS_DOMAIN_ID=0`;
- задаёт `ROS2_WASHER_ROOT` для CSV-логгера;
- после создания запускает `rosdep` и `colcon build`.

Для графического Gazebo/RViz Docker Desktop должен иметь рабочий WSLg/Wayland или X-сервер. В текущей конфигурации X11-блок `runArgs` закомментирован, так как Dev Containers автоматически добавляет Wayland-сокет WSLg.

### Сборка вручную

```powershell
docker pull osrf/ros:jazzy-desktop-full
docker build -t washer-robot:jazzy .
```

Образ большой. При ошибке `failed to fetch oauth token: ... EOF` проблема обычно связана с временным доступом Docker Desktop к Docker Hub. Повторите `docker pull`, перезапустите Docker Desktop или проверьте proxy/VPN/credential helper.

## 9. Установка и сборка без контейнера

На Ubuntu 24.04:

```bash
sudo apt update
sudo apt install -y \
  ros-jazzy-ros-gz \
  ros-jazzy-slam-toolbox \
  ros-jazzy-navigation2 \
  ros-jazzy-nav2-bringup \
  ros-jazzy-teleop-twist-keyboard \
  ros-jazzy-rviz2 \
  python3-yaml \
  xterm
```

Сборка:

```bash
source /opt/ros/jazzy/setup.bash
cd ~/ros2_washer_robot
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

После изменения `package.xml` или `CMakeLists.txt` повторите `colcon build`. Для изменений Python/launch-файлов в symlink-сборке обычно достаточно перезапустить launch.

## 10. Запуск полной симуляции

### Режим клавиатуры

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_washer_robot/install/setup.bash
ros2 launch washer_navigation full_simulation.launch.py mode:=keyboard
```

В окне `teleop_twist_keyboard` используются стандартные клавиши пакета. Для экстренной остановки можно отправить нулевую скорость:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist '{}'
```

### Режим сценария

Измените `src/washer_teleop/config/mission.yaml`, затем запустите:

```bash
ros2 launch washer_navigation full_simulation.launch.py mode:=script
```

В этом режиме клавиатурный teleop не запускается. `velocity_controller.py` последовательно исполняет команды YAML.

## 11. Запуск компонентов отдельно

```bash
ros2 launch washer_gazebo sim.launch.py
ros2 launch washer_navigation slam.launch.py
ros2 launch washer_teleop teleop.launch.py mode:=keyboard
ros2 run washer_navigation trajectory_logger.py
rviz2 -d src/washer_navigation/rviz/slam.rviz
```

Такой режим полезен для диагностики: можно отдельно проверить Gazebo, bridge, SLAM или teleop.

## 12. Полезные команды диагностики

```bash
ros2 node list
ros2 topic list
ros2 topic info /cmd_vel
ros2 topic echo /odom --once
ros2 topic echo /scan --once
ros2 run tf2_tools view_frames
ros2 run tf2_ros tf2_echo map base_link
ros2 service list | grep slam
ros2 service type /slam_toolbox/save_map
ros2 topic echo /map --once
```

## 13. Ожидаемые topic и frame

| Имя | Тип | Источник или назначение |
|---|---|---|
| `/cmd_vel` | `geometry_msgs/msg/Twist` | Команды скорости роботу |
| `/odom` | `nav_msgs/msg/Odometry` | Одометрия из Gazebo |
| `/scan` | `sensor_msgs/msg/LaserScan` | Данные лидара |
| `/map` | `nav_msgs/msg/OccupancyGrid` | Карта от SLAM Toolbox |
| `/tf` | `tf2_msgs/msg/TFMessage` | Дерево трансформаций |
| `/clock` | `rosgraph_msgs/msg/Clock` | Время Gazebo |
| `/robot_description` | `std_msgs/msg/String` | URDF робота |
| `/slam_toolbox/trajectory` | `nav_msgs/msg/Path` | Траектория SLAM, если опубликована установленной версией slam_toolbox |

## 14. Сохранение результатов

Карты сохраняйте в `src/washer_navigation/maps/`.

Логи траектории находятся в `src/washer_navigation/logs/`.

Оба каталога создаются во время запуска. Карты и CSV исключены из Git, чтобы не добавлять автоматически созданные бинарные и временные файлы в репозиторий.

## 15. Частые проблемы

### Робот не появляется в Gazebo

```bash
colcon build --symlink-install
source install/setup.bash
ros2 pkg prefix washer_description
```

Если Gazebo сообщает `invalid poses` или `The solution of LCP includes NAN values`, сначала пересоберите workspace после изменений URDF:

```bash
colcon build --symlink-install --packages-select washer_description washer_gazebo
source install/setup.bash
```

В URDF у каждого динамического link должна быть положительная масса и корректная положительно определённая инерция. В этой версии добавлена инерция лидара, исправлены инерции колёс, добавлено небольшое демпфирование joints, а робот при спавне поднят на 0.50 м для исключения начального проникновения колёс и caster в пол.

### В RViz нет карты

Проверьте `/scan`, `/odom`, `/clock` и TF:

```bash
ros2 topic echo /scan --once
ros2 topic echo /odom --once
ros2 run tf2_ros tf2_echo odom base_link
```

SLAM запускается с `use_sim_time: true`, поэтому bridge должен публиковать `/clock`.

### Робот не двигается

```bash
ros2 topic info /cmd_vel
ros2 topic echo /cmd_vel
```

В keyboard-режиме нужен работающий `xterm`. В headless-среде используйте режим `script` или запускайте teleop в отдельном терминале без GUI-обёртки.

### Ошибка Docker Hub при сборке

Если в логе есть `failed to fetch oauth token` или `EOF`, сбой произошёл до выполнения строк Dockerfile: Docker не получил metadata базового образа. Выполните:

```powershell
docker login
docker pull osrf/ros:jazzy-desktop-full
```

При необходимости перезапустите Docker Desktop и повторите `Dev Containers: Rebuild Container`.

## 16. Ограничения текущей реализации

- Это симуляция SLAM, а не полноценный стек автономной навигации: Nav2-планирование и costmap в запуск не включены.
- `cleaning_environment.world` является альтернативным world-файлом; полная сцена используется из `cleaning_environment.sdf`.
- `teleop_twist_keyboard` запускается через `xterm -e`, поэтому keyboard-режим требует графического окружения.
- Доступность `/slam_toolbox/trajectory` зависит от версии и параметров установленного SLAM Toolbox; CSV-логгер независимо пишет данные из `/odom`.
- Перед реальным запуском желательно проверить SDF/URDF и bridge в конкретной версии Gazebo Harmonic внутри контейнера.

## 17. Проверка исходников

Быстрые проверки, не требующие ROS 2:

```powershell
python -m py_compile (Get-ChildItem src -Filter *.py -Recurse).FullName
python -c "import xml.etree.ElementTree as ET; from pathlib import Path; [ET.parse(str(p)) for p in Path('src').rglob('*.xml')]; [ET.parse(str(p)) for p in Path('src').rglob('*.urdf')]; [ET.parse(str(p)) for p in Path('src').rglob('*.sdf')]; print('XML/URDF/SDF: OK')"
```

Полная проверка запуска выполняется только внутри Ubuntu 24.04/ROS 2 Jazzy или собранного Dev Container.
