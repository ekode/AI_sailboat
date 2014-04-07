# 
# Sailboat Environment
# 
# Provides a world environment to simulate sailing.
# Uses polar coordinates
# Angle is standardized in radians in the range [-pi, pi]
#
# Authors: Jonathan Hudgins <jhudgins8@gatech.edu>, Igor Negovetic
#
 
# standard libs
from math import *
import random

# project libs
import utilsmath
import true_sailboat
import plot

class environment:

    # --------
    # init: 
    #   creates the environment
    #       wind_prevailing: prevailing wind (velocity, angle)
    #       wind_distribution: distribution (std. dev.) of wind (velocity, angle)
    #       wind_variability: proportion to change the wind each frame
    #       measurement_error: proportion of measurement error (distance, angle)
    #       num_landmarks: number of random landmarks
    #       num_course_marks: number of course marks (excluding start and finish gates) to cross
    #       course_range: size of course (radius extent)
    #
    def __init__(self, wind_prevailing=None, wind_distribution=None, wind_variability=0.02, measurement_error=0.05,
            num_landmarks=5, num_course_marks=5, course_range=100):

        self.wind_prevailing = wind_prevailing
        self.wind_distribution = wind_distribution
        self.wind_variability = wind_variability
        self.measurement_error = measurement_error
        self.course_range = course_range

        # set reasonable defaults based on random when None is specified
        if self.wind_prevailing == None:
            self.wind_prevailing = (random.random(), utilsmath.random_angle())

        if self.wind_distribution == None:
            self.wind_distribution = (0.1, pi / 4)

        self.landmarks = []
        for i in range(num_landmarks):
            radius = random.random() * self.course_range
            angle = (random.random()-0.5) * 2 * pi
            self.landmarks.append((radius, angle))

        # create a semi random course
        self.__create_random_course(num_course_marks)

        # todo: calculate initial wind
        self.current_wind = self.wind_prevailing

    def __create_random_course(self, num_course_marks):
        # create start gate ~10 units wide
        start_angle = utilsmath.random_angle() 
        start2_angle = utilsmath.normalize_angle(start_angle + atan2(10.0, self.course_range))
        self.course = [] 
        self.course.append((0.98 * self.course_range, start_angle, True))
        self.course.append((0.98 * self.course_range, start2_angle, False))

        # todo: fill in random course spots

        end_angle = utilsmath.normalize_angle(start_angle + pi)
        end2_angle = utilsmath.normalize_angle(end_angle + atan2(10.0, self.course_range))
        self.course.append((0.98 * self.course_range, end_angle, False))
        self.course.append((0.98 * self.course_range, end2_angle, True))


    # ------------
    # add_boat:
    #   add a boat at the start
    #   give enough space if this is an additional boat
    #   return id (index) of boat
    #
    def add_boat(self):
        # todo: create a boat at start location
        # todo: add to boat list
        # todo: return boat index
        pass

    # wind:
    #   return current wind velocity and direction
    def wind(self):
        return self.current_wind

    # update:
    #   update the environment
    def update(self):
        # todo: update wind (1-a)*current + a*new_random (based on prevailing and distribution)
        # todo: upate all boat positions
        pass

    # measure_landmark:
    #   return the location (radius, angle) of the landmark and measurement relative to the sailboat (distance, angle)
    #       sailboat: the sailboat to make measurements
    #       landmark_index: the index of landmark to measure
    def measure_landmark(self, sailboat, landmark_index):
        # todo: calculate actual distance, angle
        # todo: adjust actual by measurement error
        return ((1.0, 0.0), (1.0, 0.0))

    # measure_boom:
    #   return the angle of the boom for specified sailboat_index
    #       sailboat_index: index of sail boat to measure
    def measure_boom(self, sailboat_index):
        # todo: return boom angle for sailboat_index
        return 0
    
    # measure_rudder:
    #   return the angle of the rudder for specified sailboat_index
    #       sailboat_index: index of sail boat to measure
    def measure_rudder(self, sailboat_index):
        # todo: return rudder angle for sailboat_index
        return 0

    # adjust_boom:
    #   return the angle of the boom for specified sailboat_index
    #       sailboat_index: index of sail boat to adjust
    #       delta_angle: angle to adjust the boom
    def adjust_boom(self, sailboat_index, delta_angle):
        # todo: return boom angle for sailboat_index
        return 0

    # adjust_rudder:
    #   return the angle of the rudder for specified sailboat_index
    #       sailboat_index: index of sail boat to adjust
    #       delta_angle: angle to adjust the rudder
    def adjust_rudder(self, sailboat_index, delta_angle):
        # todo: return rudder angle for sailboat_index
        return 0
    
    # next_marks:
    #   return the list of remaining marks on the course the specified boat must pass (and which side)
    #       sailboat_index: index of sail boat to adjust
    #       returns: ((radius0, angle0, to_port), ...)
    def next_marks(self, sailboat_index):
        # todo: return rudder angle for sailboat_index
        return (10, 0, True),


    def plot(self):
        plotter = plot.plot()
        plotter.start()

        # draw arrow for start direction
        mid_start_angle = utilsmath.normalize_angle((self.course[0][1] + self.course[1][1]) / 2)
        far_dist = self.course[0][0]
        near_dist = self.course[0][0] - self.course_range / 10.
        plotter.arrow((mid_start_angle, far_dist), (mid_start_angle, near_dist))

        for mark in self.course:
            plotter.mark(mark[0], mark[1], mark[2])

        for landmark in self.landmarks:
            plotter.landmark(landmark)

        plotter.show()

    
# if environment.py is run as a script, run some tests
if __name__== '__main__':
    env = environment()
    env.plot()

