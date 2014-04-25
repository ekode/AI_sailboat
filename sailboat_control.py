#
# Sailboat Agent
#
# Provides a sailboat_control class for creating sailboat agents.
# Sailboat agent performs localization and executes controls of the sailboat
#
# Authors: Jonathan Hudgins <jhudgins8@gatech.edu>, Igor Negovetic <igorilla@gmail.com>
#

import utilsmath
import matrix
import sim_config

class sailboat_control:

    def __init__(self, env):
        self.env = env
        self.boat_id = self.env.create_boat()
        self.believed_location = (0.0, 0.0)
        self.believed_heading = 0.0
        self.believed_velocity = (0.0, 0.0)
        self.measured_location = (0.0, 0.0)
        self.measured_heading = 0.0
        self.relative_wind_angle = 0.0

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
        self.measured_location, self.measured_heading = self.env.boats[self.boat_id].provide_measurements()

        if self.believed_location == (0.0, 0.0):
            self.believed_location = self.measured_location  # initial believed location

    def localize(self):
        self.boat_measure()

        # todo: implement localization
        # self.believed_location = self.measured_location
        self.kalman()

        self.believed_heading = self.measured_heading


        self.relative_wind_angle = utilsmath.normalize_angle(self.believed_heading - self.env.current_wind[1])

        pass

    def plan(self):
        # todo: implement planning
        pass

    def kalman(self):
        x = matrix.matrix([[self.believed_location[0]], [self.believed_location[1]], [self.believed_velocity[0]], [self.believed_velocity[1]]])
        u = matrix.matrix([[0.0], [0.0], [0.0], [0.0]])  # external motion

        P = matrix.matrix([[0., 0., 0., 0.], [0., 0., 0., 0.], [0., 0., 1000., 0.], [0., 0., 0., 1000.]])  # initial uncertainty
        F = matrix.matrix([[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]])  # next state function
        H = matrix.matrix([[1., 0., 0., 0.], [0., 1., 0., 0.]])  # measurement function
        R = matrix.matrix([[0.1, 0.], [0., 0.1]])  # measurement uncertainty
        I = matrix.matrix([[1., 0., 0., 0.], [0., 1., 0., 0.], [0., 0., 1., 0.], [0., 0., 0., 1.]])  # identity matrix

        # prediction
        x = (F * x) + u
        P = F * P * F.transpose()

        # measurement update
        Z = matrix.matrix([[self.measured_location[0]], [self.measured_location[1]]])
        y = Z - (H * x)
        S = H * P * H.transpose() + R
        K = P * H.transpose() * S.inverse()
        x = x + (K * y)
        P = (I - (K * H)) * P  # prediction

        self.believed_location = (x.value[0][0], x.value[1][0])
        self.believed_velocity = (x.value[2][0], x.value[3][0])
        pass
