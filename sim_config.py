#
# Sailboat Simulation Parameters
#
# Authors: Jonathan Hudgins <jhudgins8@gatech.edu>, Igor Negovetic <igorilla@gmail.com>
#


from math import *
import utilsmath

# --------
# Simulation
#
max_nr_of_steps = 200  # Maximum number of steps simulation is allowed to run


# --------
# Display
#
print_boat_data = True
print_boat_belief = True
print_env_data = True
print_wind_change = False
plot_crossings = False


# --------
# Boats
#
nr_of_boats = 1


# --------
# Error
#
location_radius_error = 0.01  # Error Factor
location_bearing_error = 3.14 / 128  # +/- Error
speed_error = 0.01  # Error Factor
heading_error = 3.14 / 128  # +/- Error
course_marker_error = 0.05
boom_measure_error = utilsmath.rad(5)
boom_control_error = utilsmath.rad(5)
rudder_measure_error = utilsmath.rad(0)
rudder_control_error = utilsmath.rad(0)


# --------
# Environment
#
# Wind
wind_prevailing = (15, utilsmath.rad(64. - 180.))  # Set to None for random prevailing wind. Otherwise set to tuple (speed, direction).
#wind_prevailing = 15, 0
wind_max = 20  # Maximum wind speed in mph for randomly chosen prevailing wind.
wind_min = 5  # Minimum wind speed in mpg for randomly chosen prevailing wind.
# wind_speed_sigma = 1.0  # Standard deviation for wind speed.
# wind_direction_sigma = 3.14 / 16.0  # Standard deviation for wind direction.
wind_speed_sigma = 0.0  # Standard deviation for wind speed.
wind_direction_sigma = 0.0  # Standard deviation for wind direction.
wind_change_rate = 300  # Nr of time steps. Wind change will be spread across this many time steps. Integer, >=1
#
# Course
course_range = 100
num_landmarks = 5
num_course_marks = 5
mark_buffer_distance = 10
smooth_dist = 7.0 # make sure this is less than the mark_buffer_distance

#
# Boat control params
max_rudder = utilsmath.rad(85)
cte_ratio = (utilsmath.rad(5.0), utilsmath.rad(10.0), 0.0)
