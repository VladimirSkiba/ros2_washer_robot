#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import sys, select, termios, tty

settings = None

'''Настройки управления '''
bindings = {
    'w': (0.3, 0.0),   # Вперёд
    's': (-0.3, 0.0),  # Назад
    'a': (0.0, 0.5),   # Влево (поворот)
    'd': (0.0, -0.5),  # Вправо (поворот)
    ' ': (0.0, 0.0),   # СТОП (Пробел)
    'k': (0.0, 0.0),   # Стоп (альтернатива)
}


def get_key():
    global settings
    # Отключаем обработку ввода терминалом
    tty.setraw(sys.stdin.fileno())
    # Читаем ввод с интервалом 0.1
    rlist, _, _ = select.select([sys.stdin], [], [], 1)
    if rlist:
        key = sys.stdin.read(1)  # Читаем один символ
        if key == '\x03':
            raise KeyboardInterrupt
    else:
        key = ''
    # Восстанавливаем настройки терминала
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key


def main():
    global settings
    rclpy.init()
    node = Node('keyboard_control')
    pub = node.create_publisher(Twist, '/cmd_vel', 10)

    settings = termios.tcgetattr(sys.stdin) # сохраняем настройки терминала 

    print("Управление:")
    print("W - вперёд")
    print("S - назад")
    print("A - влево")
    print("D - вправо")
    print("SPACE/K - стоп")
    print("Ctrl+C - выход\n")

    try:
        while rclpy.ok():
            key = get_key()
            if key in bindings:
                linear, angular = bindings[key]
                twist = Twist()
                twist.linear.x = linear
                twist.angular.z = angular
                print(f"Отправлено: linear={linear}, angular={angular}")
                pub.publish(twist)
            rclpy.spin_once(node, timeout_sec=0.1)
            
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        # Восстанавливаем терминал
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        
        # Останавливаем робот
        twist = Twist()
        pub.publish(twist)
        
        node.destroy_node()
        rclpy.shutdown()      
    


if __name__ == '__main__':
    main()
