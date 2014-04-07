from math import *

class sailboat_control:

    def __init__(self, env):
        self.env = env
        self.boat_id = self.env.create_boat()

    # return (boom_adjust_angle, rudder_adjust_angle)
    def boat_action(self):
        self.boat_measure()

        # todo: calculate desired adjustments
        return (0, 0)

    def boat_measure(self):
        # todo: use landmark measurements to calculate where I am
        for landmark in self.env.landmarks:
            (radius, angle) = self.env.measure_landmark(self.boat_id, landmark)
