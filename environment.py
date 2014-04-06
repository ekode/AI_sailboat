# 
# Sailboat Environment
# 
# Provides a world environment to simulate sailing.
# Uses polar coordinates
# Angle is standardized in radians in the range [-pi, pi]
#
# Authors: Jonathan Hudgins <jhudgins8@gatech.edu>, Igor Negovetic
#
 
from math import *
import random

class environment:

    # --------
    # init: 
    #   creates the environment
    #       wind_prevailing: prevailing wind (velocity, angle)
    #       wind_distribution: distribution (std. dev.) of wind (velocity, angle)
    #       wind_variability: proportion to change the wind each frame
    #       measurement_error: proportion of measurement error (distance, angle)
    #       landmarks: list of landmarks ((radius0, angle0), ...)
    #       course: list of course bouys ((radius0, angle0, pass_on_right), ...)
    #
    def __init__(self, wind_prevailing=None, wind_distribution=None, wind_variability=0.02, measurement_error=0.05,
                    landmarks=None, course=None):

        self.wind_prevailing = wind_prevailing
        self.wind_distribution = wind_distribution
        self.wind_variability = wind_variability
        self.measurement_error = measurement_error
        self.landmarks = landmarks
        self.course = course

        # set reasonable defaults based on random when None is specified
        if self.wind_prevailing == None:
            self.wind_prevailing = (random.random(), (random.random()-0.5) * 2 * pi)

        if self.wind_distribution === None:
            self.wind_distribution = (0.1, pi / 4)

        if self.landmarks == None:
            for i in range(10):
                self.landmarks = (random.random() * 100, (random.random()-0.5) * 2 * pi)

        # todo: create a semi random course
        if self.course == None:
            pass

        # todo: calculate initial wind
        self.current_wind = self.wind_prevailing


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
    
