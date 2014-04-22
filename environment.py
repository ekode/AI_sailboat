# 
# Sailboat Environment
# 
# Provides a world environment to simulate sailing.
# Uses polar coordinates
# Angle is standardized in radians in the range [-pi, pi]
#
# Authors: Jonathan Hudgins <jhudgins8@gatech.edu>, Igor Negovetic <igorilla@gmail.com>
#
 
# standard libs
from math import *
import random

# project libs
import utilsmath
import true_sailboat
import plot
import sim_config

class course_mark:
    def __init__(self, dist, angle, to_port):
        self.dist = dist
        self.angle = angle
        self.to_port = to_port

class environment:

    # --------
    # init: 
    #   creates the environment
    #
    def __init__(self):

        self.start_heading = 0.0
        self.course = []

        # set reasonable defaults based on random when None is specified
        if sim_config.wind_prevailing is None:
            self.wind_prevailing = (random.uniform(sim_config.wind_min, sim_config.wind_max), utilsmath.random_angle())

        # todo: potentially remove landmarks? Since we have course markers, what do we need land markers for?
        # jhudgins: I think we can get more interesting results by separating landmarks from course markers.
        #           This way we can change the number of landmarks and see how it effects the simulation.
        self.landmarks = []
        for i in range(sim_config.num_landmarks):
            radius = random.random() * sim_config.course_range
            angle = (random.random()-0.5) * 2 * pi
            self.landmarks.append((radius, angle))

        # create a semi random course
        self.__create_random_course()

        self.boats = []

        self.current_wind = self.wind_prevailing


    def __create_random_course(self):
        # create start gate ~10 units wide

        start_angle = utilsmath.random_angle()

        start2_angle = utilsmath.normalize_angle(start_angle + atan2(10.0, sim_config.course_range))
        self.start_heading = utilsmath.normalize_angle(start_angle + pi)
        self.course = []
        self.course.append(course_mark(0.98 * sim_config.course_range, start_angle, True))
        self.course.append(course_mark(0.98 * sim_config.course_range, start2_angle, False))

        end_angle = utilsmath.normalize_angle(start_angle + pi)
        end2_angle = utilsmath.normalize_angle(end_angle + atan2(10.0, sim_config.course_range))
        end_starboard_mark = course_mark(0.98 * sim_config.course_range, end_angle, False)
        end_port_mark = course_mark(0.98 * sim_config.course_range, end2_angle, True)
        end_port_loc = [end_port_mark.dist, end_port_mark.angle]

        # intermediate course markers
        prev_mark_loc = [self.course[0].dist, self.course[0].angle]
        angle_flip = 1
        for count in range(sim_config.num_course_marks):

            # calculate control variables based on how many marks we have left
            remaining_marks = sim_config.num_course_marks - count
            dist_to_end, angle_to_end = utilsmath.calculate_distance_angle(prev_mark_loc, end_port_loc)
            dist_btwn = random.uniform(0.8, 1.5) * dist_to_end / remaining_marks
            angle_btwn = utilsmath.normalize_angle(random.random() * angle_flip * utilsmath.rad(70) + angle_to_end)

            mark_loc = utilsmath.add_vectors_polar(prev_mark_loc, [dist_btwn, angle_btwn])
            self.course.append(course_mark(mark_loc[0], mark_loc[1], angle_flip==-1))

            prev_mark_loc = mark_loc
            angle_flip *= -1

        self.course.append(end_starboard_mark)
        self.course.append(end_port_mark)

    # ------------
    # create_boat:
    #   create a true world representation of boat at the start
    #   give enough space if this is an additional boat
    #   return id (index) of boat
    #
    def create_boat(self):
        mid_start_angle = utilsmath.normalize_angle((self.course[0].angle + self.course[1].angle) / 2)
        start_dist = self.course[0].dist
        boat = true_sailboat.true_sailboat((start_dist, mid_start_angle), self.start_heading)
        self.boats.append(boat)
        if sim_config.print_boat_data:
            print 'initializing boat', len(self.boats)-1, boat.location, 'heading', boat.heading

        return len(self.boats) - 1

    # wind:
    #   return current wind speed and direction
    def wind(self):
        return self.current_wind

    # change_wind
    #   change wind speed and direction
    def change_wind(self):
        # todo: implement change_wind
        # todo: update wind (1-a)*current + a*new_random (based on prevailing and distribution)
        new_wind = self.current_wind

        return new_wind

    # update:
    #   update the environment
    def update(self, controls):

        if sim_config.print_env_data:
            print ' '
            print 'wind', self.current_wind

        for boat_id, control, boat in zip(range(len(controls)), controls, self.boats):
            boat.updateControls(control)
            boat.update(self)
            self.plotter.true_boat(boat.location)

            if sim_config.print_boat_data:
                print ' '
                print 'boat', boat_id
                print 'position', boat.location
                print 'heading', boat.heading
                print 'wind angle', boat.relative_wind_angle
                print 'speed', boat.speed


    # measure_landmark:
    #   return the measurement relative to the sailboat (distance, angle)
    #       boat_id: the id of the true_sailboat to make measurements
    #       landmark: the landmark to measure
    def measure_landmark(self, boat_id, landmark):
        boat = self.boats[boat_id]
        measurement = utilsmath.calculate_distance_angle(boat.location, landmark)
        radius_error = random.gauss(1, sim_config.course_marker_error)
        angle_error = random.gauss(1, sim_config.course_marker_error)
        return measurement[0] * radius_error, measurement[1] * angle_error

    # measure_boom:
    #   return the angle of the boom for specified sailboat_index
    #       sailboat_index: index of sail boat to measure
    def measure_boom(self, sailboat_index):
        measured_boom = self.boats[sailboat_index].boom + random.gauss(0, sim_config.boom_measure_error)
        return utilsmath.normalize_angle(measured_boom)
    
    # measure_rudder:
    #   return the angle of the rudder for specified sailboat_index
    #       sailboat_index: index of sail boat to measure
    def measure_rudder(self, sailboat_index):
        measured_rudder = self.boats[sailboat_index].rudder + random.gauss(0, sim_config.rudder_measure_error)
        return utilsmath.normalize_angle(measured_rudder)

    # next_marks:
    #   return the list of remaining marks on the course the specified boat must pass (and which side)
    #       sailboat_index: index of sail boat to adjust
    #       returns: ((radius0, angle0, to_port), ...)
    def next_marks(self, sailboat_index):
        # todo: return remaining marks
        return (10, 0, True),


    def plot(self):
        self.plotter = plot.plot()
        self.plotter.start()

        # draw arrow for start direction
        mid_start_angle = utilsmath.normalize_angle((self.course[0].angle + self.course[1].angle) / 2)
        far_dist = self.course[0].dist
        near_dist = self.course[0].dist - sim_config.course_range / 10.
        self.plotter.arrow((mid_start_angle, far_dist), (mid_start_angle, near_dist))

        count = 0
        for mark in self.course:
            plotCount = -1
            if count not in [0, 1, len(self.course)-2, len(self.course)-1]:
                plotCount = count - 2

            self.plotter.mark(mark, plotCount)
            count += 1

        for landmark in self.landmarks:
            self.plotter.landmark(landmark)

    
# if environment.py is run as a script, run some tests
if __name__ == '__main__':
    env = environment()
    env.plot()

    boat_id = env.create_boat()
    env.measure_landmark(boat_id, env.landmarks[0])

    env.plotter.true_boat(env.boats[boat_id].location)

    # test measurement function
    env.plotter.line(env.boats[boat_id].location, env.landmarks[0])
    measurement = env.measure_landmark(boat_id, env.landmarks[0])
    print "boat to landmark:{0}".format(utilsmath.format_location(measurement))

    env.plotter.show()

