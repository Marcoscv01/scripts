#!/usr/bin/env python3
import rospy
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist
from tf.transformations import euler_from_quaternion
import math

# Variables globales
x = 0.0
y = 0.0
yaw = 0.0

# Parámetros
SIDE_LENGTH = 0.2  # 20 cm
ANGLE = 72 * math.pi / 180  # ángulo exterior del pentágono

KP_ANG = 1.5
KP_LIN = 0.5

def get_odom(msg):
    global x, y, yaw

    x = msg.pose.pose.position.x
    y = msg.pose.pose.position.y

    orientation_q = msg.pose.pose.orientation
    (_, _, yaw) = euler_from_quaternion([
        orientation_q.x,
        orientation_q.y,
        orientation_q.z,
        orientation_q.w
    ])

def normalize_angle(angle):
    return math.atan2(math.sin(angle), math.cos(angle))

def rotate_to_angle(pub, target_angle):
    global yaw
    rate = rospy.Rate(10)
    cmd = Twist()

    while not rospy.is_shutdown():
        error = normalize_angle(target_angle - yaw)

        if abs(error) < 0.01:
            break

        cmd.angular.z = KP_ANG * error
        pub.publish(cmd)
        rate.sleep()

    pub.publish(Twist())

def move_straight(pub, start_x, start_y):
    global x, y, yaw
    rate = rospy.Rate(10)
    cmd = Twist()

    while not rospy.is_shutdown():
        dx = x - start_x
        dy = y - start_y
        distance = math.sqrt(dx**2 + dy**2)

        error = SIDE_LENGTH - distance

        if error < 0.01:
            break

        cmd.linear.x = KP_LIN * error
        pub.publish(cmd)
        rate.sleep()

    pub.publish(Twist())

if __name__ == "__main__":
    rospy.init_node("muevePentagono")

    rospy.Subscriber("/odom", Odometry, get_odom)
    pub = rospy.Publisher("/cmd_vel", Twist, queue_size=1)

    rospy.sleep(1)

    for i in range(5):
        # Guardar posición inicial
        start_x = x
        start_y = y

        # Avanzar lado
        move_straight(pub, start_x, start_y)

        # Girar
        target_angle = yaw + ANGLE
        target_angle = normalize_angle(target_angle)
        rotate_to_angle(pub, target_angle)

    rospy.loginfo("Pentágono completado")