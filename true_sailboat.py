# 
# Sailboat
# 
# Provides a true_sailboat which simulates the real (unknown to the robot)
# position and heading of the boat
#
# Authors: Jonathan Hudgins <jhudgins8@gatech.edu>, Igor Negovetic
#
 
from math import *
import random

class true_sailboat:

    # --------
    # init: 
    #   creates the true_sailboat
    #       location: (radius, bearing, heading)
    #       boom_control_error: proportion of boom control error (see adjust_boom)
    #       rudder_control_error: proportion of rudder control error (see adjust_rudder)
    #
    def __init__(self, location, boom_control_error, rudder_control_error):
        self.location = location
        self.boom = 0
        self.rudder = 0
        self.boom_control_error = boom_control_error
        self.rudder_control_error = rudder_control_error
        self.gate_index = 0


    # ----------
    # update:
    # update the true_sailboat location based on the environment
    def update(self, env):
        # todo: implement
        pass

    # ------------
    # adjust_boom:
    # adjust the boom angle (relative to current)
    def adjust_boom(self, boom_adjustment):
        # todo: implement
        pass

    # --------------
    # adjust_rudder:
    # adjust the rudder angle (relative to current)
    def adjust_rudder(self, rudder_adjustment):
        # todo: implement
        pass
