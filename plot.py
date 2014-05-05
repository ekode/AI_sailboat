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
import sim_config
import utilsmath


can_plot = False
try:
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    can_plot = True
except ImportError, e:
    print "No plotting because: {0}".format(e)
    print "  Windows: try downloading from http://www.lfd.uci.edu/~gohlke/pythonlibs/#matplotlib"
    print "  Linux: use 'sudo apt-get install python-matplotlib'"

class plot:

    # --------
    # init: 
    #   creates the plot object
    #   initializes if libraries are available
    #
    def __init__(self):
        pass

    def start(self):
        global can_plot
        if not can_plot:
            return

        self.fig = plt.figure(figsize=(15, 15))
        self.subplot = self.fig.add_subplot(111, polar=True, navigate=True)
        plt.ion()  # enable interactive plotting

    def end(self):
        plt.ioff()

    def show(self):
        global can_plot
        if not can_plot:
            return

        plt.show()
        #self.fig.show(block=True)

    def draw(self):
        plt.draw()
        #self.fig.draw()

    def plot_course(self, env, polar_plot):

        # draw arrow for start direction
        mid_start_angle = utilsmath.normalize_angle((env.course[0].angle + env.course[1].angle) / 2)
        far_dist = env.course[0].radius
        near_dist = env.course[0].radius - sim_config.course_range / 10.
        polar_plot.arrow((far_dist, mid_start_angle), (near_dist, mid_start_angle))

        count = 0
        for mark in env.course:
            plotCount = -1
            if count not in [0, 1, len(env.course), len(env.course)-1]:
                plotCount = count - 2

            polar_plot.mark(mark, plotCount)

            # plot crossings
            if sim_config.plot_crossings:
                crossColors = ['goldenrod', 'cyan']
                for color, crossing in zip(crossColors, mark.crossings):
                    crossing_end = utilsmath.add_vectors_polar([mark.radius, mark.angle], [15, crossing[1]])
                    polar_plot.arrow((mark.radius, mark.angle), crossing_end, color=color)

            count += 1

    def mark(self, mark, count):
        global can_plot
        if not can_plot:
            return

        # conform to standards from http://www.sailing.org/tools/documents/ISAFRRS20132016Final-[13376].pdf
        if mark.to_port:
            color = 'red'
            shape = 's' # square
        else: # starboard
            color = 'green'
            shape = '^' # triagle up

        self.subplot.plot(mark.angle, mark.radius, color=color, marker=shape)

        if count != -1:
            self.subplot.text(mark.angle, mark.radius+2., '{0}'.format(count), color=color)

    def arrow(self, start, finish, color='black'):
        global can_plot
        if not can_plot:
            return

        #self.subplot.annotate("", xytext=start, xy=finish, arrowprops=dict(arrowstyle="->", facecolor='g'))
        self.subplot.annotate("", xytext=(start[1], start[0]), xy=(finish[1], finish[0]), arrowprops=dict(arrowstyle="->", color=color))

    def true_boat(self, location):
        global can_plot
        if not can_plot:
            return

        self.subplot.plot(location[1], location[0], color='black', marker='x')

    def boat_belief(self, location):
        global can_plot
        if not can_plot:
            return

        self.subplot.plot(location[1], location[0], color='red', marker='x')

    def boat_measured(self, location):
        global can_plot
        if not can_plot:
            return

        self.subplot.plot(location[1], location[0], color='green', marker='x')

    def line(self, loc1, loc2, color='black'):
        global can_plot
        if not can_plot:
            return

        self.subplot.plot((loc1[1], loc2[1]), (loc1[0], loc2[0]), color=color)


