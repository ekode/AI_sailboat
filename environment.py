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
    def __init__(self, radius, angle, to_port):
        self.radius = radius
        self.angle = angle
        self.to_port = to_port
        self.crossings = []


class environment:

    # --------
    # init: 
    #   creates the environment
    #
    def __init__(self):

        self.start_heading = 0.0
        self.course = []

        # Set wind variables
        if sim_config.wind_prevailing is None:
            self.wind_prevailing = (random.uniform(sim_config.wind_min, sim_config.wind_max), utilsmath.random_angle())
        else:
            self.wind_prevailing = sim_config.wind_prevailing
        self.current_wind = self.wind_prevailing  # (speed, direction)
        self.wind_speed_change = 0
        self.wind_direction_change = 0
        self.goal_wind = (0, 0)  # new wind, used only for reporting and troubleshooting

        # create a semi random course
        self.__create_random_course()
        self.__calculate_mark_crossings()

        self.boats = []  # True boats


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
        end_port_loc = [end_port_mark.radius, end_port_mark.angle]

        # intermediate course markers
        prev_mark_loc = [self.course[0].radius, self.course[0].angle]
        angle_flip = 1
        for count in range(sim_config.num_course_marks):

            # calculate control variables based on how many marks we have left
            remaining_marks = sim_config.num_course_marks - count + 1
            dist_to_end, angle_to_end = utilsmath.sub_vectors_polar(end_port_loc, prev_mark_loc)
            dist_btwn = random.uniform(0.8, 1.5) * dist_to_end / remaining_marks
            angle_btwn = utilsmath.normalize_angle(random.random() * angle_flip * utilsmath.rad(45) + angle_to_end)

            mark_loc = utilsmath.add_vectors_polar(prev_mark_loc, [dist_btwn, angle_btwn])
            self.course.append(course_mark(mark_loc[0], mark_loc[1], angle_flip==-1))

            prev_mark_loc = mark_loc
            angle_flip *= -1

        # end with correct port/starboard
        if angle_flip==-1:
            self.course.append(end_port_mark)
            self.course.append(end_starboard_mark)
        else:
            self.course.append(end_starboard_mark)
            self.course.append(end_port_mark)

    def __calculate_mark_crossings(self):
        for i in range(2, len(self.course)-1):
            prev_mark = self.course[i-1]
            this_mark = self.course[i]
            next_mark = self.course[i+1]

            # cross through bisector of this_prev and this_next going ccw/cw if this_mark is port/starboard
            this_prev = utilsmath.sub_vectors_polar([prev_mark.radius, prev_mark.angle],
                                                            [this_mark.radius, this_mark.angle])
            this_next = utilsmath.sub_vectors_polar([next_mark.radius, next_mark.angle],
                                                            [this_mark.radius, this_mark.angle])
            if this_mark.to_port:
                angle = utilsmath.cw(this_next[1] - this_prev[1])
            else:
                angle = utilsmath.ccw(this_next[1] - this_prev[1])

            # 0 length for first crossing means any distance acceptable
            # cross through this_next (within the length from this to next)
            this_mark.crossings = [(0, utilsmath.normalize_angle(angle/2.0 + this_prev[1])), this_next]


    # ------------
    # create_boat:
    #   create a true world representation of boat at the start
    #   give enough space if this is an additional boat
    #   return id (index) of boat
    #
    def create_boat(self):
        mid_start_angle = utilsmath.normalize_angle((self.course[0].angle + self.course[1].angle) / 2)
        start_dist = self.course[0].radius
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
    def change_wind(self, i):
        # Set new wind speed and direction every sim_config.wind_change_rate number of steps
        if i % sim_config.wind_change_rate == 0:
            new_wind_speed = self.wind_prevailing[0] + random.gauss(0, sim_config.wind_speed_sigma)
            new_wind_direction = self.wind_prevailing[1] + random.gauss(0, sim_config.wind_direction_sigma)
            self.goal_wind = (new_wind_speed, new_wind_direction)
            self.wind_speed_change = (new_wind_speed - self.current_wind[0]) / sim_config.wind_change_rate
            self.wind_direction_change = (new_wind_direction - self.current_wind[1]) / sim_config.wind_change_rate

        # Change the wind for the current step little bit towards the new wind speed and direction
        new_wind = (self.current_wind[0] + self.wind_speed_change,
                    utilsmath.normalize_angle(self.current_wind[1] + self.wind_direction_change))

        self.current_wind = new_wind
        pass

    # update:
    #   update the environment
    def update(self, controls):

        for boat_id, control, boat in zip(range(len(controls)), controls, self.boats):
            #self.plotter.true_boat(boat.location)
            boat.updateControls(control)
            boat.update(self)

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

    # update_mark:
    #   return the index of the updated mark
    #
    # In above diagram, if current mark (cM) is a port side mark, we need to cross the line nM->cM on the
    # port side (by the ^^^)
    #
    def update_mark(self, prevLoc, currentLoc, mark_index):
        pass



    # next_marks:
    #   return the list of remaining marks on the course the specified boat must pass (and which side)
    #       sailboat_index: index of sail boat to adjust
    #       returns: ((radius0, angle0, to_port), ...)
    def next_marks(self, sailboat_index):
        # todo: return remaining marks
        return (10, 0, True),


    def plot(self):
        # todo: this was moved to plot.py. Perhaps remove from here?
        self.plotter = plot.plot()
        self.plotter.start()

        # draw arrow for start direction
        mid_start_angle = utilsmath.normalize_angle((self.course[0].angle + self.course[1].angle) / 2)
        far_dist = self.course[0].radius
        near_dist = self.course[0].radius - sim_config.course_range / 10.
        self.plotter.arrow((far_dist, mid_start_angle), (near_dist, mid_start_angle))

        count = 0
        for mark in self.course:
            plotCount = -1
            if count not in [0, 1, len(self.course), len(self.course)-1]:
                plotCount = count - 2

            self.plotter.mark(mark, plotCount)

            # plot crossings
            if sim_config.plot_crossings:
                crossColors = ['goldenrod', 'cyan']
                for color, crossing in zip(crossColors, mark.crossings):
                    crossing_end = utilsmath.add_vectors_polar([mark.radius, mark.angle], [15, crossing[1]])
                    self.plotter.arrow((mark.radius, mark.angle) , crossing_end, color=color)

            count += 1

    def is_finished(self, i):
        # todo: implement finish line detection. Keep in mind possibility of multiple boats.
        if i >= sim_config.max_nr_of_steps:
            return True
        else:
            return False

    
# if environment.py is run as a script, run some tests
if __name__ == '__main__':
    import pdb; pdb.set_trace()
    env = environment()
    env.plot()

    boat_id = env.create_boat()

    env.plotter.true_boat(env.boats[boat_id].location)

    env.plotter.show()

