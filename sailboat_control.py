#
# Sailboat Agent
#
# Provides a sailboat_control class for creating sailboat agents.
# Sailboat agent performs localization and executes controls of the sailboat
#
# Authors: Jonathan Hudgins <jhudgins8@gatech.edu>, Igor Negovetic <igorilla@gmail.com>
#

from math import *
import utilsmath

class sailboat_control:

    def __init__(self, env):
        self.env = env
        self.boat_id = self.env.create_boat()
        self.location = (0, 0)
        self.heading = 0
        self.relative_wind_angle = 0

    # return (boom_adjust_angle, rudder_adjust_angle)
    def boat_action(self):
        self.localize()
        self.plan()

        # todo: calculate new rudder and boom angles
        # for now, just turn the boat slightly down-wind
        if self.relative_wind_angle < 0.0:
            rudder = 0.2
        else:
            rudder = -0.2

        boom = 0.0

        return boom, rudder


    def boat_measure(self):
        # todo: use landmark measurements to calculate where I am
        for landmark in self.env.landmarks:
            (radius, angle) = self.env.measure_landmark(self.boat_id, landmark)


        self.location, self.heading = self.env.boats[self.boat_id].provide_measurements()
        pass


    def localize(self):
        self.boat_measure()

        # todo: implement localization

        self.relative_wind_angle = utilsmath.normalize_angle(self.heading - self.env.current_wind[1])

        pass


    def plan(self):
        # todo: implement planning
        pass