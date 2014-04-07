# 
# Math Utils for Sailboat project
# 
# Authors: Jonathan Hudgins <jhudgins8@gatech.edu>, Igor Negovetic
#
 
import random
from math import *

def normalize_angle(angle):
    while (angle < -pi):
        angle += 2*pi
    while (angle > pi):
        angle -= 2*pi
    return angle

def random_angle():
    return (random.random()-0.5) * 2 * pi
