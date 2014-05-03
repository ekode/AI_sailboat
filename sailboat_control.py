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
import environment
import scipy.optimize
from math import *
import random
random.seed(123)

class sailboat_control:

    def __init__(self, env):
        self.env = env
        self.boat_id = self.env.create_boat()
        self.believed_location = (0.0, 0.0)
        self.believed_heading = 0.0
        self.believed_velocity = (0.0, 0.0)
        self.prev_believed_location = None
        self.measured_location = (0.0, 0.0)
        self.measured_heading = 0.0
        self.relative_wind_angle = 0.0
        self.mark_state = environment.mark_state(2, 0)

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
        self.prev_believed_location = self.believed_location
        self.kalman()

        self.believed_heading = self.measured_heading


        self.relative_wind_angle = utilsmath.normalize_angle(self.believed_heading - self.env.current_wind[1])


    def __update_mark_state(self):
        if self.prev_believed_location:
            self.env.update_mark_state(self.prev_believed_location, self.believed_location, self.mark_state)

    def __way_point(self, mark, crossing):
        # is this the first entry of a course_mark
        if crossing[0] == 0:
            delta = [sim_config.mark_buffer_distance, crossing[1]]
        else:
            delta = [crossing[0]/2.0, crossing[1]]
        return utilsmath.add_vectors_polar([mark.radius, mark.angle], delta)

    def __calculate_way_points(self):
        self.way_points = []
        mark_index = self.mark_state.index
        crossing_index = self.mark_state.crossing_index
        while mark_index < len(self.env.course):
            # get the mark
            mark = self.env.course[mark_index]

            # skip the mark if it has no crossings
            if len(mark.crossings) == 0:
                mark_index += 1
                continue

            # append the way point
            crossing = mark.crossings[crossing_index]
            self.way_points.append(self.__way_point(mark, crossing))

            # advance to next crossing (advance mark if we have visited all of this mark's crossings)
            crossing_index += 1
            if crossing_index >= len(mark.crossings):
                crossing_index = 0
                mark_index += 1

    def plot_plan(self):
        last_way_point = self.believed_location
        for way_point in self.way_points:
            self.env.plotter.line(last_way_point, way_point, color='magenta')
            last_way_point = way_point

        last_tack = self.believed_location
        for tack in self.tacking:
            self.env.plotter.line(last_tack, tack, color='blue')
            last_tack = tack


    def __calculate_optimal_tack(self, to_port, desired_angle):

        wind_angle = self.env.current_wind[1]
        def directional_speed(delta_angle):
            true_angle = delta_angle + desired_angle
            stall_ratio = 0.05
            speed_ratio = (1.0 + stall_ratio) * e**(-(abs(true_angle - wind_angle)**2)/2) - stall_ratio
            directional_speed = cos(delta_angle) * speed_ratio
            return -directional_speed

        bounds = (0.0, pi/2.0) if to_port else (-pi/2.0, 0.0)
        best_angle = scipy.optimize.minimize_scalar(directional_speed, bounds=bounds, method='bounded')
        return utilsmath.normalize_angle(best_angle.x + desired_angle)

    def __calculate_intermediates(self, last_location, to_waypoint, port_optimal_angle, starboard_optimal_angle):
        # Only tack if one of the optimal angles isn't straight to waypoint
        # There might be a more optimal route if we tack on the optimal in one direction and then
        # use sub-optimal in the other direction, but for now just keep it simple.
        if utilsmath.approx_equal(port_optimal_angle, to_waypoint[1]) or utilsmath.approx_equal(starboard_optimal_angle, to_waypoint[1]):
            return []

        # find linear combination of v1, v2 that will equal to_waypoint
        # [v1x   v2x] [ a1 ] =  [ to_wx ]
        # [v1y   v2y] [ a2 ] =  [ to_wy ]

        v1 = utilsmath.polar_to_euclidean([1.0, port_optimal_angle])
        v2 = utilsmath.polar_to_euclidean([1.0, starboard_optimal_angle])
        to_w = utilsmath.polar_to_euclidean(to_waypoint)
        a = utilsmath.solve2dLinear(v1[0], v2[0], v1[1], v2[1], to_w[0], to_w[1])

        # it might be helpful to do a number of tacks with these considerations:
        #       cost of changing heading / momentum
        #       next desired angle after way_point
        #       spatial restrictions
        #       wind variability
        #
        # But for now just tack once

        v0 = utilsmath.polar_to_euclidean(last_location)
        return [utilsmath.euclidean_to_polar((a[0]*v1[0] + v0[0], a[0]*v1[1] + v0[1]))]


    # micro planning (tacking)
    def __calculate_tacking(self):
        last_location = self.believed_location
        self.tacking = []
        for way_point in self.way_points:
            # check optimal angle on port/starboard side of desired direction to next way_point
            to_waypoint = utilsmath.sub_vectors_polar(way_point, last_location)

            intermediates = self.__calculate_intermediates(last_location, to_waypoint,
                                                            port_optimal_angle, starboard_optimal_angle)
            self.tacking += intermediates
            self.tacking.append(way_point)
            last_location = way_point


    def plan(self):
        self.__update_mark_state()
        self.__calculate_way_points()
        self.__calculate_tacking()


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
