# 
# Math Utils for Sailboat project
# 
# Authors: Jonathan Hudgins <jhudgins8@gatech.edu>, Igor Negovetic <igorilla@gmail.com>
#
 
import random
from math import *
import matrix


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
    v1x, v1y = polar_to_cartesian(v1)
    v2x, v2y = polar_to_cartesian(v2)

    rx = v1x + v2x
    ry = v1y + v2y

    return cartesian_to_polar((rx, ry))


def sub_vectors_polar(v1, v2):
    return add_vectors_polar(v1, (-v2[0], v2[1]))


def polar_to_cartesian(p):
    return p[0]*cos(p[1]), p[0]*sin(p[1])


def cartesian_to_polar(c):
    return hypot(c[0], c[1]), atan2(c[1], c[0])


# calculate distance for two points given in polar coordinates
def distance_polar(a, b):
    return sqrt(a[0]**2 + b[0]**2 - 2*a[0]*b[0]*cos(a[1] - b[1]))


def solve2dLinear(a, b, c, d, e, f):
    # [a  b]  [x]  =  [e]
    # [c  d]  [y]  =  [f]
    #
    # Note: I tried the matrix library inverse, but it gave me: "Matrix not positive-definite" for some values
    # So I just use the simple inverse formula for 2x2
    #        -1
    # [ a b ]    = 1/det * [ d  -b ]
    # [ c d ]              [ -c  a ]
    #
    det = a * d - b * c
    if abs(det) < 1e-10:
        import pdb;pdb.set_trace()
        raise ValueError, "Invalid determinant"

    solution = ((d*e-b*f) / det, (-c*e+a*f) / det)
    return solution


# determine intesection   of line starting at l1 in direction and length of v1
#                       with line starting at l2 in direction and length of v2
# note: if v1 or v2 have 0 radius - we assume this is an infinite ray
def intersect(l1in, v1in, l2in, v2in):
    # make local copies so that we don't update values of in parameters
    l1 = list(l1in)
    l2 = list(l2in)
    v1 = list(v1in)
    v2 = list(v2in)

    # check for parallel lines
    if abs(v1[1] - v2[1]) < 1e-40 or abs(normalize_angle(v1[1] - v2[1] - pi)) < 1e-40:

        # these can only be coincident if l1l2 is also parallel
        l1l2 = sub_vectors_polar(l2, l1)
        if abs(l1l2[1] - v1[1]) > 1e-40 and abs(normalize_angle(l1l2[1] - v1[1] - pi)) > 1e-40:
            return False
        else:
            raise ValueError, "Test for coincident lines not complete -- rare in practice"

    isV1Ray = (v1[0] == 0)
    isV2Ray = (v2[0] == 0)
    if isV1Ray:
        v1[0] = 1
    if isV2Ray:
        v2[0] = 1

    l1 = polar_to_cartesian(l1)
    v1 = polar_to_cartesian(v1)
    l2 = polar_to_cartesian(l2)
    v2 = polar_to_cartesian(v2)


    # s1 = l1 + a1 * v1   for 0 <= a1 <= 1
    # s2 = l2 + a2 * v2   for 0 <= a2 <= 1
    #
    # solve for  a1 and a2
    #
    # [v1x   -v2x] [a1] = [l2x - l1x]
    # [v1y   -v2y] [a2] = [l2y - l1y]

    a = solve2dLinear(v1[0], -v2[0], v1[1], -v2[1], l2[0] - l1[0], l2[1] - l1[1])

    if a[0] < 0 or a[1] < 0:
        return False
    if not isV1Ray and a[0] > 1:
        return False
    if not isV2Ray and a[1] > 1:
        return False

    return True



# if utilsmath.py is run as a script, run some tests
if __name__== '__main__':
    tests = []
    test = ["Testing normalize_angle", 0, 0]
    print test[0]
    for (test_angle, result_angle) in [(rad(-270), rad(90)), (rad(270), rad(-90)), (rad(360), rad(0))]:
        test[1] += 1
        actual_angle = normalize_angle(test_angle) 
        passed = result_angle == actual_angle
        if passed:
            test[2] += 1
        print "  normalize_angle({0:.0f}) = {1:.0f} ?= {2:.0f}: {3}".format(deg(test_angle), deg(actual_angle),
                                                                deg(result_angle), passed)
    tests.append(test)
    print

    test = ["Testing sub_vectors_polar", 0, 0]
    print test[0]
    distance_tests = [((1, 0), (1, rad(60)), (1, rad(-60))),
                        ((2, rad(-120)), (1, rad(60)), (3, rad(-120)))]
    for (l1, l2, result) in distance_tests:
        test[1] += 1
        actual = sub_vectors_polar(l1, l2)
        passed = approx_equal(actual[0], result[0]) and approx_equal(actual[1], result[1])
        if passed:
            test[2] += 1
        print "  sub_vectors_polar({0}, {1}) = {2} ?= {3} : {4}".format(format_location(l1), format_location(l2),
                                            format_location(actual), format_location(result), passed)
    tests.append(test)
    print

    test = ["Testing Intersection", 0, 0]
    testSamples = (([0, 0], [1, 0], [1, -rad(45)], [1, rad(90)], True),
                    ([0, 0], [1, 0], [1, -rad(45)], [1, rad(0)], False),
                    ([0, 0], [1, 0], [1, -rad(45)], [1, rad(1e-40)], False),
                    ([0, 0], [1, 0], [1, -rad(45)], [1, rad(0.1)], False),
                    ([0, 0], [1, 0], [1, -rad(45)], [1./sqrt(2.) - 0.001, rad(90)], False),
                    ([0, 0], [1, 0], [1, -rad(45)], [1./sqrt(2.) + 0.001, rad(90)], True),
                    ([0, 0], [1, 0], [1, -rad(45)], [0, rad(90)], True))
    for testSample in testSamples:
        test[1] += 1
        result = intersect(testSample[0], testSample[1], testSample[2], testSample[3])
        if result == testSample[-1]:
            test[2] += 1
            print "  Intersection test {0} passed".format(testSample)
        else:
            print "  Intersection test {0} FAILED!".format(testSample)
    tests.append(test)
    print

    testSuccesses = 0
    for test in tests:
        if test[1] == test[2]:
            testSuccesses += 1
            print "PASSED:",
        else:
            print "FAILED:",
        print "{0} -- {1} out of {2} correct".format(test[0], test[2], test[1])

    print
    if testSuccesses == len(tests):
        print "PASSED!"
    else:
        print "FAILED!"
