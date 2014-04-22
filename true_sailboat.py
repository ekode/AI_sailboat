# 
# Sailboat
# 
# Provides a true_sailboat which simulates the real (unknown to the robot)
# position and heading of the boat
#
# Authors: Jonathan Hudgins <jhudgins8@gatech.edu>, Igor Negovetic <igorilla@gmail.com>
#
 
from math import *
import random
import utilsmath
import sim_config

class true_sailboat:

    # --------
    # init: 
    #   creates the true_sailboat
    #       location: (radius, bearing)
    #       heading: boat heading
    #       boom: current boom angle
    #       rudder: current rudder angle
    #       max_speed_ratio: maximum boat speed under ideal conditions, as a proportion of current wind speed
    #       relative_wind_angle: angle of the wind relative to boat's heading
    #       speed: boat's current speed
    #
    def __init__(self, location, heading=pi/2.0, max_speed_ratio=0.7,
                                                            boom_control_error=sim_config.boom_control_error,
                                                            boom_measure_error=sim_config.boom_measure_error,
                                                            rudder_control_error=sim_config.rudder_control_error,
                                                            rudder_measure_error=sim_config.rudder_measure_error):
        self.location = location
        self.heading = heading
        self.boom = 0
        self.rudder = 0
        self.max_speed_ratio = max_speed_ratio
        self.relative_wind_angle = 0
        self.speed = 0
        self.boom_measure_error = boom_measure_error
        self.boom_control_error = boom_control_error
        self.rudder_measure_error = rudder_measure_error
        self.rudder_control_error = rudder_control_error
        self.gate_index = 0

    # ----------
    # updateControls:
    # update controls based on desired deltas
    def updateControls(self, controls):
        if controls[0] != 0:
            self.boom = utilsmath.normalize_angle(self.boom + controls[0] + random.gauss(0, self.boom_control_error))

        if controls[1] != 0:
            self.rudder = utilsmath.normalize_angle(self.boom + controls[1] +random.gauss(0, self.rudder_control_error))

    # ----------
    # update:
    # update the true_sailboat location based on the environment
    def update(self, env):
        # Velocity vector will be added to boat's current position vector in order to calculate the new position.
        # Magnitude of the velocity vector is boat's speed. Direction of the velocity vector is boat's heading,
        # adjusted for rudder
        self.heading = utilsmath.normalize_angle(self.heading + self.rudder/2.0)


        # Boat's speed depends on the angle at which wind is blowing at the boat, wind strength, and boom angle
        # todo: implement considering boom angle
        self.relative_wind_angle = utilsmath.normalize_angle(self.heading - env.current_wind[1])
        self.speed = self.calculate_speed(self.relative_wind_angle, env.current_wind[0], self.boom)

        # Determine velocity direction
        if self.speed <= 0.0:
            # Boat stalled. Rotate it.
            if self.relative_wind_angle < 0.0:
                # Rotate boat counter-clockwise at the rate proportional to wind strength
                self.heading = utilsmath.normalize_angle(self.heading + env.current_wind[0]*0.01)
            else:
                # Rotate boat clockwise at the rate proportional to wind strength
                self.heading = utilsmath.normalize_angle(self.heading - env.current_wind[0]*0.01)
        else:
            self.adjust_heading()

        # Add velocity vector to the boat's location vector to create new location
        v1 = self.location
        v2 = (self.speed, self.heading)
        self.location = (utilsmath.add_vectors_polar(v1, v2))

    # --------------
    # adjust_heading:
    # adjust heading based on the rudder angle. Rudder angle goes from -pi/2 to pi. See plan.txt for more details.
    def adjust_heading(self):
        # Simplified model: Change heading half amount of the rudder angle.
        self.heading = utilsmath.normalize_angle(self.heading + self.rudder/2.0)

    # --------------
    # calculate_speed:
    def calculate_speed(self, wind_angle, wind_strength, boom):
        # todo: add boom angle into calculation. Current calculation reflects ideal boom position. Any other boom should reduce the speed.
        # Boat's maximum possible speed given the wind depends on the boat's heading relative to the wind direction.
        # We assume that the boat is fastest when sailing directly down-wind (run), slower if the wind comes from the
        # sides (reach), the boat stalls and even moves backwards (while slowly turning around) if he wind is head-on.

        max_speed = self.max_speed_ratio * wind_strength
        stall_range = 0.05 * max_speed

        # Using normal distribution function
        speed = (max_speed + stall_range)*e**(-(wind_angle**2)/2) - stall_range

        return speed

    # --------------
    # provide_measurements:
    # supply noisy measurements of location and heading to the boat agent
    def provide_measurements(self):

        # Location
        if sim_config.location_error == 0:
            location = self.location
        else:
            # todo: add error to location measurement
            location = self.location

        # Heading
        if sim_config.heading_error == 0:
            heading = self.heading
        else:
            # todo: add error to heading measurement
            heading = self.heading

        return location, heading
