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

        self.fig = plt.figure()
        self.subplot = self.fig.add_subplot(111, polar=True)

    def show(self):
        global can_plot
        if not can_plot:
            return

        plt.show()

    def mark(self, radius, angle, to_port):
        global can_plot
        if not can_plot:
            return

        # conform to standards from http://www.sailing.org/tools/documents/ISAFRRS20132016Final-[13376].pdf
        if to_port:
            color = 'red'
            shape = 's' # square
        else: # starboard
            color = 'green'
            shape = '^' # triagle up

        self.subplot.plot(angle, radius, color=color, marker=shape)

    def arrow(self, start, finish, color='black'):
        global can_plot
        if not can_plot:
            return

        #self.subplot.annotate("", xytext=start, xy=finish, arrowprops=dict(arrowstyle="->", facecolor='g'))
        self.subplot.annotate("", xytext=start, xy=finish, arrowprops=dict(arrowstyle="->", color=color))

    def landmark(self, location):
        global can_plot
        if not can_plot:
            return

        self.subplot.plot(location[1], location[0], color='white', marker='o')

    def true_boat(self, location):
        global can_plot
        if not can_plot:
            return

        self.subplot.plot(location[1], location[0], color='black', marker='x')


    def line(self, loc1, loc2, color='black'):
        global can_plot
        if not can_plot:
            return

        self.subplot.plot((loc1[1], loc2[1]), (loc1[0], loc2[0]), color=color)


