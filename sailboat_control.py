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
        self.believed_velocity_cart = (0.0, 0.0)
        self.measured_location_cart = (0.0, 0.0)
        self.measured_heading = 0.0
        self.relative_wind_angle = 0.0

        # Kalman filter variables

        self.kalman_u = matrix.matrix([[0.0], [0.0], [0.0], [0.0]])  # external motion
        self.kalman_P = matrix.matrix([[0., 0., 0., 0.], [0., 0., 0., 0.], [0., 0., 1000., 0.], [0., 0., 0., 1000.]])  # initial uncertainty
        self.kalman_F = matrix.matrix([[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]])  # next state function
        self.kalman_H = matrix.matrix([[1., 0., 0., 0.], [0., 1., 0., 0.]])  # measurement function
        self.kalman_R = matrix.matrix([[0.01, 0.], [0., 0.01]])  # measurement uncertainty
        self.kalman_I = matrix.matrix([[1., 0., 0., 0.], [0., 1., 0., 0.], [0., 0., 1., 0.], [0., 0., 0., 1.]])  # identity matrix

        """
        self.kalman_u = matrix.matrix([[0.0], [0.0]])  # external motion
        self.kalman_P = matrix.matrix([[1000., 0.], [0., 1000.]])  # initial uncertainty
        self.kalman_F = matrix.matrix([[1, 1], [0, 1]])  # next state function
        self.kalman_H = matrix.matrix([[1., 0.]])  # measurement function
        self.kalman_R = matrix.matrix([[0.01]])  # measurement uncertainty
        self.kalman_I = matrix.matrix([[1., 0.], [0., 1.]])  # identity matrix
        """

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

        rudder = 0.0
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


    def plan(self):
        # todo: implement planning
        pass

    def kalman(self):

        # Convert polar coordinates to cartesian
        c = utilsmath.polar_to_cartesian(self.believed_location)
        m = utilsmath.polar_to_cartesian(self.measured_location)

        x = matrix.matrix([[c[0]], [c[1]], [self.believed_velocity_cart[0]], [self.believed_velocity_cart[1]]])
        ### x = matrix.matrix([[self.believed_location[0]], [self.believed_location[1]], [self.believed_velocity[0]], [self.believed_velocity[1]]])
        ### x = matrix.matrix([[self.believed_location[0]], [self.believed_velocity[0]]])

        # prediction
        x = (self.kalman_F * x) + self.kalman_u
        self.kalman_P = self.kalman_F * self.kalman_P * self.kalman_F.transpose()

        # measurement update
        Z = matrix.matrix([[m[0]], [m[1]]])
        ### Z = matrix.matrix([[self.measured_location[0]], [self.measured_location[1]]])
        ### Z = matrix.matrix([[self.measured_location[0]]])
        y = Z - (self.kalman_H * x)
        S = self.kalman_H * self.kalman_P * self.kalman_H.transpose() + self.kalman_R
        K = self.kalman_P * self.kalman_H.transpose() * S.inverse()
        x = x + (K * y)
        self.kalman_P = (self.kalman_I - (K * self.kalman_H)) * self.kalman_P  # prediction

        self.believed_location = (utilsmath.cartesian_to_polar((x.value[0][0], x.value[1][0])))
        self.believed_velocity_cart = (x.value[2][0], x.value[3][0])
        ### self.believed_location = (x.value[0][0], utilsmath.normalize_angle(x.value[1][0]))
        ### self.believed_velocity = (x.value[2][0], utilsmath.normalize_angle(x.value[3][0]))
        ### self.believed_location = (x.value[0][0], self.measured_location[1])
        ### self.believed_velocity = (x.value[1][0], 0.)
