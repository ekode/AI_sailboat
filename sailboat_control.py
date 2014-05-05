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
        self.measured_rudder = 0.0
        self.relative_wind_angle = 0.0
        self.mark_state = environment.mark_state(2, 0)
        self.replan = True
        self.last_cross_track_error = 0.0
        self.int_cross_track_error = 0.0

    # return (boom_adjust_angle, rudder_adjust_angle)
    def boat_action(self):
        self.localize()
        if self.replan:
            self.plan()

        return self.controls()

    def controls(self):
        projection_ratio, cross_track_error = self.__calculate_cte()
        if projection_ratio >= 0:
            diff_cross_track_error = cross_track_error - self.last_cross_track_error
            self.int_cross_track_error += cross_track_error

            desired_rudder = -cross_track_error * sim_config.cte_ratio[0]
            desired_rudder += -diff_cross_track_error * sim_config.cte_ratio[1]
            desired_rudder += -self.int_cross_track_error * sim_config.cte_ratio[2]
        else:
            to_next_tack = utilsmath.sub_vectors_polar(self.tacking[self.tacking_index+1], self.tacking[self.tacking_index])
            desired_heading = to_next_tack[1]
            desired_rudder = desired_heading - self.believed_heading


        rudder_delta = utilsmath.normalize_angle(desired_rudder - self.measured_rudder)

        self.last_cross_track_error = cross_track_error

        boom = 0.0

        return boom, rudder_delta

    def boat_measure(self):
        self.measured_location, self.measured_heading = self.env.boats[self.boat_id].provide_measurements()

        if self.believed_location == (0.0, 0.0):
            self.believed_location = self.measured_location  # initial believed location

        self.measured_rudder = self.env.boats[self.boat_id].measure_rudder()

    def localize(self):
        self.boat_measure()

        # todo: implement localization
        # self.believed_location = self.measured_location
        self.prev_believed_location = self.believed_location
        self.kalman()

        self.believed_heading = self.measured_heading


        self.relative_wind_angle = utilsmath.normalize_angle(self.believed_heading - self.env.current_wind[1])


    # calculate the projection onto the expected line segment and distance from that segment
    def __calculate_projection_distance(self):
        if self.tacking_index + 1 >= len(self.tacking):
            return 0.0, 0.0

        tack_start = utilsmath.polar_to_euclidean(self.tacking[self.tacking_index])
        tack_end = utilsmath.polar_to_euclidean(self.tacking[self.tacking_index + 1])
        xy_location = utilsmath.polar_to_euclidean(self.believed_location)

        segment_vec = [tack_end[0]-tack_start[0], tack_end[1]-tack_start[1]]
        segment_len = sqrt(segment_vec[0] ** 2 + segment_vec[1] ** 2)
        location_vec = [xy_location[0] - tack_start[0], xy_location[1] - tack_start[1]]
        location_len = sqrt(location_vec[0] ** 2 + location_vec[1] ** 2)

        # use 0, 0 if location is at start point
        if location_len == 0:
            return (0, 0)

        projection_ratio = (segment_vec[0] * location_vec[0] + segment_vec[1] * location_vec[1]) / (segment_len ** 2)
        distance = (-segment_vec[1] * location_vec[0] + segment_vec[0] * location_vec[1]) / segment_len

        return (projection_ratio, distance)


    # calculate the cross track error
    # if the project is greater than 1, then we have crossed the end of this tack point: increment tacking_index
    # and recalculate cte
    def __calculate_cte(self):
        projection_ratio, distance = self.__calculate_projection_distance()
        # check if we have crossed the end of this tacking
        if projection_ratio > 1.0:
            self.tacking_index += 1
            projection_ratio, distance = self.__calculate_projection_distance()
        return projection_ratio, distance



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


    # find the angle on port or starboard side of desired angle that give the best speed
    # limit the angle to +/- pi/2
    def __calculate_optimal_tack(self, to_port, desired_angle):

        wind_angle = self.env.current_wind[1]

        # this is our estimate of speed in the direction of desired_angle
        # returns -speed to allow scipy to optimize (find minimum)
        def directional_speed(delta_angle):
            true_angle = delta_angle + desired_angle
            stall_ratio = 0.05
            speed_ratio = (1.0 + stall_ratio) * e**(-(abs(true_angle - wind_angle)**2)/2) - stall_ratio
            directional_speed = cos(delta_angle) * speed_ratio
            return -directional_speed

        bounds = (0.0, pi/2.0) if to_port else (-pi/2.0, 0.0)
        best_angle = scipy.optimize.minimize_scalar(directional_speed, bounds=bounds, method='bounded')
        return utilsmath.normalize_angle(best_angle.x + desired_angle)


    # choose the angle closest to the base angle
    # return (best, other)
    def __choose_angles(self, base, angle1, angle2):
        delta1 = abs(utilsmath.normalize_angle(base - angle1))
        delta2 = abs(utilsmath.normalize_angle(base - angle2))
        return (angle1, angle2) if delta1 < delta2 else (angle2, angle1)

    def __is_angle_close(self, angle1, angle2, threshhold):
        return abs(utilsmath.normalize_angle(angle1 - angle2)) < threshhold

    # find intermediate points between way_points
    # we want to make sure we start and end close to the desired direction
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

        v1 = utilsmath.polar_to_euclidean([1.0, start_tack])
        v2 = utilsmath.polar_to_euclidean([1.0, middle_tack1])
        to_w = utilsmath.polar_to_euclidean(to_waypoint)
        a = utilsmath.solve2dLinear(v1[0], v2[0], v1[1], v2[1], to_w[0], to_w[1])

        v0 = utilsmath.polar_to_euclidean(last_location)

        # if we end our turn at a different angle than we start than we just need to tack once
        if start_tack != last_tack:
            return [utilsmath.euclidean_to_polar((a[0]*v1[0] + v0[0], a[0]*v1[1] + v0[1]))]
        # if we end our turn at the same angle than we need to tack twice, so that we end up with a heading
        # closest to the next desired heading
        else:
            # use the midpoint of the v1 to tack, sail v2 fully, then tack back to the remainder of v1
            point1 = (a[0]*v1[0]*0.5 + v0[0], a[0]*v1[1]*0.5 + v0[1])
            point2 = (a[1]*v2[0] + point1[0], a[0]*v2[1] + point1[1])
            return [utilsmath.euclidean_to_polar(point1), utilsmath.euclidean_to_polar(point2)]
             

    # micro planning (tacking)
    def __calculate_tacking(self):
        last_location = self.believed_location
        self.tacking = [self.believed_location]
        prev_heading = self.believed_velocity[1]
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

    def __smooth_tacking(self):
        smoothed = [self.tacking[0]]
        prev_point = utilsmath.polar_to_euclidean(self.tacking[0])
        for i in range(1, len(self.tacking)-1):
            # smooth the corners just a bit
            this_point = utilsmath.polar_to_euclidean(self.tacking[i])
            next_point = utilsmath.polar_to_euclidean(self.tacking[i+1])
            v1 = [this_point[0] - prev_point[0], this_point[1] - prev_point[1]]
            v2 = [next_point[0] - this_point[0], next_point[1] - this_point[1]]
            v1_len = sqrt(v1[0]**2 + v1[1]**2)
            v2_len = sqrt(v2[0]**2 + v2[1]**2)

            # offset away from the corner (just a bit)
            smooth_offset1 = [v1[0]/v1_len * sim_config.smooth_dist, v1[1]/v1_len * sim_config.smooth_dist]
            smooth_offset2 = [v2[0]/v2_len * sim_config.smooth_dist, v2[1]/v2_len * sim_config.smooth_dist]
            p1 = [this_point[0] - smooth_offset1[0], this_point[1] - smooth_offset1[1]]
            p2 = [this_point[0] + smooth_offset2[0], this_point[1] + smooth_offset2[1]]

            # add an average point of all three
            pavg = [(this_point[0] + p1[0] + p2[0]) / 3.0, (this_point[1] + p1[1] + p2[1]) / 3.0]
            smoothed.append(utilsmath.euclidean_to_polar(p1))
            smoothed.append(utilsmath.euclidean_to_polar(pavg))
            smoothed.append(utilsmath.euclidean_to_polar(p2))

            prev_point = this_point

        smoothed.append(self.tacking[-1])
        self.tacking = smoothed



    def plan(self):
        self.__update_mark_state()
        self.__calculate_way_points()
        self.__calculate_tacking()
        # smoothing is minor but helps enough for some cases that were going off the rails!
        self.__smooth_tacking()
        # reset tacking index
        self.tacking_index = 0
        self.replan = False

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
