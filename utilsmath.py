# 
# Math Utils for Sailboat project
# 
# Authors: Jonathan Hudgins <jhudgins8@gatech.edu>, Igor Negovetic <igorilla@gmail.com>
#
 
import random
from math import *


def normalize_angle(angle):
    # maps angle onto [-pi, pi]
    while (angle < -pi):
        angle += 2*pi
    while (angle > pi):
        angle -= 2*pi
    return angle


def random_angle():
    return (random.random()-0.5) * 2 * pi

def ccw(angle):
    while (angle < -2*pi):
        angle += 2*pi
    while angle > 0:
        angle -= 2*pi
    return angle

def cw(angle):
    while (angle > 2*pi):
        angle -= 2*pi
    while angle < 0:
        angle += 2*pi
    return angle


def deg(angle):
    return (angle / pi * 180.)


def rad(angle):
    return (angle / 180. * pi)


def format_location(loc):
    return "({0}, {1:.1f}deg)".format(loc[0], deg(loc[1]))


def approx_equal(v1, v2):
    return abs(v1 - v2) <= max(abs(v1), abs(v2)) * 0.00001


def add_vectors_polar(v1, v2):
    v1x = v1[0] * cos(v1[1])
    v1y = v1[0] * sin(v1[1])
    v2x = v2[0] * cos(v2[1])
    v2y = v2[0] * sin(v2[1])

    rx = v1x + v2x
    ry = v1y + v2y

    r = sqrt(rx**2 + ry**2)

    a = acos(rx/r)
    if ry < 0:
        a = -a

    return (r, a)

def sub_vectors_polar(v1, v2):
    return add_vectors_polar(v1, (-v2[0], v2[1]))


# if utilsmath.py is run as a script, run some tests
if __name__== '__main__':
    print "Testing normalize_angle"
    for (test_angle, result_angle) in [(rad(-270), rad(90)), (rad(270), rad(-90)), (rad(360), rad(0))]:
        actual_angle = normalize_angle(test_angle) 
        print "  normalize_angle({0:.0f}) = {1:.0f} ?= {2:.0f}: {3}".format(deg(test_angle), deg(actual_angle),
                                                                deg(result_angle), result_angle == actual_angle)
    print

    print "Testing calculate_distance_angle"
    distance_tests = [((1, rad(60)), (1, 0), (1, rad(-60))),
                        ((1, rad(60)), (2, rad(-120)), (3, rad(-120)))]
    for (l1, l2, result) in distance_tests:
        actual = calculate_distance_angle(l1, l2)
        print "  calculate_distance_angle({0}, {1}) = {2} ?= {3} : {4}".format(format_location(l1), format_location(l2),
                                            format_location(actual), format_location(result),
                                            approx_equal(actual[0], result[0]) and approx_equal(actual[1], result[1]))
