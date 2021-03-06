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
        self.measured_rudder = 0.0
        self.measured_speed = 0.0

        self.relative_wind_angle = 0.0
        self.mark_state = environment.mark_state(2, 0)
        self.replan = True
        self.last_cross_track_error = 0.0
        self.int_cross_track_error = 0.0

        # Kalman filter variables
        self.kalman_u = matrix.matrix([[0.0], [0.0], [0.0], [0.0]])  # external motion
        self.kalman_P = matrix.matrix([[0., 0., 0., 0.], [0., 0., 0., 0.], [0., 0., 0.1, 0.], [0., 0., 0., 10.]])  # initial uncertainty
        self.kalman_F = matrix.matrix([[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]])  # next state function
        self.kalman_H = matrix.matrix([[1., 0., 0., 0.], [0., 1., 0., 0.]])  # measurement function
        self.kalman_R = matrix.matrix([[0.01, 0.], [0., 0.01]])  # measurement uncertainty
        self.kalman_I = matrix.matrix([[1., 0., 0., 0.], [0., 1., 0., 0.], [0., 0., 1., 0.], [0., 0., 0., 1.]])  # identity matrix

        self.igor_target_tack = 1


    # return (boom_adjust_angle, rudder_adjust_angle)
    def boat_action(self):
        self.localize()
        if self.replan:
            self.plan()

        if sim_config.use_igor:
            return self.igor_controls()

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
            #desired_rudder = desired_heading - self.believed_heading
            desired_rudder = desired_heading - self.measured_heading

            """
            print "tacking_index:{0}".format(self.tacking_index)
            print "tacking[{0}]:{1}".format(self.tacking_index, self.tacking[self.tacking_index])
            print "tacking[{0}]:{1}".format(self.tacking_index+1, self.tacking[self.tacking_index+1])
            print "to_next_tack:{0}".format(to_next_tack)
            print "believed_heading:{0}".format(utilsmath.deg( self.believed_heading))
            print "measured_heading:{0}".format(utilsmath.deg( self.measured_heading))
            print "desired_heading:{0}".format(utilsmath.deg( desired_heading))
            print "desired_rudder:{0}".format(utilsmath.deg(desired_rudder))
            import pdb; pdb.set_trace()
            """


        rudder_delta = utilsmath.normalize_angle(desired_rudder - self.measured_rudder)

        self.last_cross_track_error = cross_track_error

        boom = 0.0

        return boom, rudder_delta


    def localize(self):
        self.measured_location, self.measured_heading, self.measured_speed = self.env.boats[self.boat_id].provide_measurements()
        self.believed_heading = self.measured_heading
        self.believed_speed = self.measured_speed
        self.measured_rudder = self.env.boats[self.boat_id].measure_rudder()

        if self.believed_location == (0.0, 0.0):
            # Initial location - do not run Kalman
            self.believed_location = self.env.boats[self.boat_id].location
        else:
            self.prev_believed_location = self.believed_location
            self.kalman()

        self.relative_wind_angle = utilsmath.normalize_angle(self.believed_heading - self.env.current_wind[1])


    # calculate the projection onto the expected line segment and distance from that segment
    def __calculate_projection_distance(self):
        if self.tacking_index + 1 >= len(self.tacking):
            return 0.0, 0.0

        tack_start = utilsmath.polar_to_cartesian(self.tacking[self.tacking_index])
        tack_end = utilsmath.polar_to_cartesian(self.tacking[self.tacking_index + 1])
        xy_location = utilsmath.polar_to_cartesian(self.believed_location)

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
        self.tacking = [self.believed_location]
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

    def __smooth_tacking(self):
        smoothed = [self.tacking[0]]
        prev_point = utilsmath.polar_to_cartesian(self.tacking[0])
        for i in range(1, len(self.tacking)-1):
            # smooth the corners just a bit
            this_point = utilsmath.polar_to_cartesian(self.tacking[i])
            next_point = utilsmath.polar_to_cartesian(self.tacking[i+1])
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
            smoothed.append(utilsmath.cartesian_to_polar(p1))
            smoothed.append(utilsmath.cartesian_to_polar(pavg))
            smoothed.append(utilsmath.cartesian_to_polar(p2))

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
        #self.believed_speed, self.believed_heading = utilsmath.cartesian_to_polar((x.value[2][0], x.value[3][0]))


    def igor_controls(self):
        # Check if you are close enough to the target tack point. If so, switch to the next tack point.
        tack_point_distance = utilsmath.distance_polar(self.believed_location, self.tacking[self.igor_target_tack])
        while tack_point_distance < 2.0:
            self.igor_target_tack += 1
            tack_point_distance = utilsmath.distance_polar(self.believed_location, self.tacking[self.igor_target_tack])

        dir = utilsmath.sub_vectors_polar(self.tacking[self.igor_target_tack], self.believed_location)
        desired_rudder = utilsmath.normalize_angle(dir[1] - self.believed_heading)

        self.measured_rudder = self.env.boats[self.boat_id].measure_rudder()

        rudder_delta = desired_rudder - self.measured_rudder

        """
        print ' '
        print 'target tack', self.igor_target_tack, self.tacking[self.igor_target_tack]
        print 'tack point distance', tack_point_distance
        #print 'alpha', alpha
        print 'dir', dir
        print 'desired rudder', desired_rudder
        print 'measured rudder', self.measured_rudder
        print 'rudder delta', rudder_delta
        """

        boom = 0.0

        return boom, rudder_delta
