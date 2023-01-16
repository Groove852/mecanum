#!/usr/bin/python3
# -*- coding: utf-8 -*-
import rclpy
from rclpy.qos import QoSProfile

from geometry_msgs.msg import Twist

import sys, select, termios, tty

settings = termios.tcgetattr(sys.stdin)

msg = """
Reading from the keyboard  and Publishing to Twist!
---------------------------
Moving around:
   q    w    e
   a    s    d
        x    

anything else : stop
z/c : increase/decrease max speeds by 10%
CTRL-C to quit
"""

moveBindings = {'w':(-1, 0, 0, 0),
                'e':(0, -1, 0, 0),
                'a':(0, 0, 0, 1),
                'd':(0, 0, 0, -1),
                'q':(0, 1, 0, 0),
                'x':(1, 0, 0, 0),}

speedBindings = {'z':(1.1, 1.1),
                 'c':(.9, .9),}

def getKey(settings):
    if sys.platform == 'win32':
        key = msvcrt.getwch()
    else:
        tty.setraw(sys.stdin.fileno())
        key = sys.stdin.read(1)
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

def saveTerminalSettings():
    if sys.platform == 'win32':
        return None
    return termios.tcgetattr(sys.stdin)


def restoreTerminalSettings(old_settings):
    if sys.platform == 'win32':
        return
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)


def vels(speed, turn):
    return 'currently:\tspeed %s\tturn %s ' % (speed, turn)


def main():
    settings = saveTerminalSettings()

    rclpy.init()

    node = rclpy.create_node('teleop_twist_keyboard')
    pub = node.create_publisher(Twist, 'cmd_vel', 10)

    speed = 0.1
    turn = 0.5
    x = 0.0
    y = 0.0
    z = 0.0
    th = 0.0
    status = 0.0

    lx = 0.0
    ly = 0.0
    lth = 0.0

    try:
        print(msg)
        print(vels(speed, turn))
        while True:
            key = getKey(settings)
            if key in moveBindings.keys():
                x = moveBindings[key][0]
                y = moveBindings[key][1]
                z = moveBindings[key][2]
                th = moveBindings[key][3]
            elif key in speedBindings.keys():
                speed = speed * speedBindings[key][0]
                turn = turn * speedBindings[key][1]

                print(vels(speed, turn))
                if (status == 14):
                    print(msg)
                status = (status + 1) % 15
            else:
                x = 0.0
                lx = 0.0
                y = 0.0
                ly = 0.0
                z = 0.0
                th = 0.0
                lth = 0.0
                if (key == '\x03'):
                    break

            twist = Twist()
            twist.linear.x = lx + (x * speed)
            twist.linear.y = ly + (y * speed)
            twist.linear.z = z * speed
            twist.angular.x = 0.0
            twist.angular.y = 0.0
            twist.angular.z = lth + (th * turn)
            lx = twist.linear.x
            ly = twist.linear.y
            lth = twist.angular.z
            pub.publish(twist)

    except Exception as e:
        print(e)

    finally:
        twist = Twist()
        twist.linear.x = 0.0
        twist.linear.y = 0.0
        twist.linear.z = 0.0
        twist.angular.x = 0.0
        twist.angular.y = 0.0
        twist.angular.z = 0.0
        pub.publish(twist)

        restoreTerminalSettings(settings)


if __name__ == '__main__':
    main()