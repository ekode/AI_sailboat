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

        #self.believed_location = self.env.boats[self.boat_id].location  # Initial believed location
        self.believed_location = 0.0, 0.0
        self.believed_heading = 0.0
        self.believed_speed = 0.0

        self.prev_believed_location = None

        self.measured_location = (0.0, 0.0)
        self.measured_heading = 0.0
        self.measured_speed = 0.0

        self.relative_wind_angle = 0.0
        self.mark_state = environment.mark_state(2, 0)

        # Kalman filter variables
        self.kalman_u = matrix.matrix([[0.0], [0.0], [0.0], [0.0]])  # external motion
        self.kalman_P = matrix.matrix([[0., 0., 0., 0.], [0., 0., 0., 0.], [0., 0., 0.1, 0.], [0., 0., 0., 10.]])  # initial uncertainty
        self.kalman_F = matrix.matrix([[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]])  # next state function
        self.kalman_H = matrix.matrix([[1., 0., 0., 0.], [0., 1., 0., 0.]])  # measurement function
        self.kalman_R = matrix.matrix([[0.01, 0.], [0., 0.01]])  # measurement uncertainty
        self.kalman_I = matrix.matrix([[1., 0., 0., 0.], [0., 1., 0., 0.], [0., 0., 1., 0.], [0., 0., 0., 1.]])  # identity matrix


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


    def localize(self):
        self.measured_location, self.measured_heading, self.measured_speed = self.env.boats[self.boat_id].provide_measurements()
        self.believed_heading = self.measured_heading
        self.believed_speed = self.measured_speed

        if self.believed_location == (0.0, 0.0):
            # Initial location - do not run Kalman
            self.believed_location = self.env.boats[self.boat_id].location
        else:
            self.prev_believed_location = self.believed_location
            self.kalman()

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

    def plot_plan(self, plotter):
        last_way_point = self.believed_location
        for way_point in self.way_points:
            #self.env.plotter.line(last_way_point, way_point, color='magenta')
            plotter.line(last_way_point, way_point, color='magenta')
            last_way_point = way_point

        last_tack = self.believed_location
        for tack in self.tacking:
            #self.env.plotter.line(last_tack, tack, color='blue')
            plotter.line(last_tack, tack, color='blue')
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


    def __choose_angles(self, base, angle1, angle2):
        delta1 = abs(utilsmath.normalize_angle(base - angle1))
        delta2 = abs(utilsmath.normalize_angle(base - angle2))
        return (angle1, angle2) if delta1 < delta2 else (angle2, angle1)

    def __is_angle_close(self, angle1, angle2, threshhold):
        return abs(utilsmath.normalize_angle(angle1 - angle2)) < threshhold

    def __calculate_intermediates(self, last_location, to_waypoint, prev_heading, next_heading):
        # check optimal angle on port/starboard side of desired direction to next way_point
        port_optimal_angle = self.__calculate_optimal_tack(True, to_waypoint[1])
        starboard_optimal_angle = self.__calculate_optimal_tack(False, to_waypoint[1])

        # Only tack if one of the optimal angles isn't straight to waypoint
        # There might be a more optimal route if we tack on the optimal in one direction and then
        # use sub-optimal in the other direction, but for now just keep it simple.
        is_port_close = self.__is_angle_close(port_optimal_angle, to_waypoint[1], utilsmath.rad(1))
        is_starboard_close = self.__is_angle_close(starboard_optimal_angle, to_waypoint[1], utilsmath.rad(1))
        if is_port_close or is_starboard_close:
            return []

        # calculate starting/last tack based on what our prev/next heading
        # middle_tack will be the other tack
        start_tack, middle_tack1 = self.__choose_angles(prev_heading, port_optimal_angle, starboard_optimal_angle)
        last_tack, middle_tack2 = self.__choose_angles(next_heading, port_optimal_angle, starboard_optimal_angle)

        # find linear combination of v1, v2 that will equal to_waypoint
        # [v1x   v2x] [ a1 ] =  [ to_wx ]
        # [v1y   v2y] [ a2 ] =  [ to_wy ]

        v1 = utilsmath.polar_to_cartesian([1.0, start_tack])
        v2 = utilsmath.polar_to_cartesian([1.0, middle_tack1])
        to_w = utilsmath.polar_to_cartesian(to_waypoint)
        a = utilsmath.solve2dLinear(v1[0], v2[0], v1[1], v2[1], to_w[0], to_w[1])

        v0 = utilsmath.polar_to_cartesian(last_location)

        # if we end our turn at a different angle than we start than we just need to tack once
        if start_tack != last_tack:
            return [utilsmath.cartesian_to_polar((a[0]*v1[0] + v0[0], a[0]*v1[1] + v0[1]))]
        # if we end our turn at the same angle than we need to tack twice, so that we end up with a heading
        # closest to the next desired heading
        else:
            # use the midpoint of the v1 to tack, sail v2 fully, then tack back to the remainder of v1
            point1 = (a[0]*v1[0]*0.5 + v0[0], a[0]*v1[1]*0.5 + v0[1])
            point2 = (a[1]*v2[0] + point1[0], a[0]*v2[1] + point1[1])
            return [utilsmath.cartesian_to_polar(point1), utilsmath.cartesian_to_polar(point2)]
             

    # micro planning (tacking)
    def __calculate_tacking(self):
        last_location = self.believed_location
        self.tacking = []
        prev_heading = self.believed_heading
        for i in range(len(self.way_points)):
            way_point = self.way_points[i]

            to_waypoint = utilsmath.sub_vectors_polar(way_point, last_location)
            if i+1 < len(self.way_points):
                ignore, next_heading = utilsmath.sub_vectors_polar(self.way_points[i+1], way_point)
                # if next_heading is close enough to the direction we are already going, skip this way_point
                if self.__is_angle_close(to_waypoint[1], next_heading, utilsmath.rad(10)):
                    # don't append anything to tacking list or update loop variables since we are skipping this waypoint
                    continue
            else:
                next_heading = to_waypoint[1]

            intermediates = self.__calculate_intermediates(last_location, to_waypoint, prev_heading, next_heading)
            
            # add intermediates to tacking list
            self.tacking += intermediates
            self.tacking.append(way_point)

            # update loop variables
            last_location = way_point
            prev_heading = to_waypoint[1]


    def plan(self):
        self.__update_mark_state()
        self.__calculate_way_points()
        self.__calculate_tacking()


    def kalman(self):

        # Convert polar coordinates to cartesian
        c = utilsmath.polar_to_cartesian(self.believed_location)
        v = utilsmath.polar_to_cartesian((self.believed_speed, self.believed_heading))
        m = utilsmath.polar_to_cartesian(self.measured_location)

        x = matrix.matrix([[c[0]], [c[1]], [v[0]], [v[1]]])

        # prediction
        x = (self.kalman_F * x) + self.kalman_u
        self.kalman_P = self.kalman_F * self.kalman_P * self.kalman_F.transpose()

        # measurement update
        Z = matrix.matrix([[m[0]], [m[1]]])
        y = Z - (self.kalman_H * x)
        S = self.kalman_H * self.kalman_P * self.kalman_H.transpose() + self.kalman_R
        K = self.kalman_P * self.kalman_H.transpose() * S.inverse()
        x = x + (K * y)
        self.kalman_P = (self.kalman_I - (K * self.kalman_H)) * self.kalman_P  # prediction

        self.believed_location = (utilsmath.cartesian_to_polar((x.value[0][0], x.value[1][0])))
        self.believed_speed, self.believed_heading = utilsmath.cartesian_to_polar((x.value[2][0], x.value[3][0]))

