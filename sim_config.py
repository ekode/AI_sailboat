#
# Sailboat Simulation Parameters
#
# Authors: Jonathan Hudgins <jhudgins8@gatech.edu>, Igor Negovetic <igorilla@gmail.com>
#


import utilsmath

# --------
# Simulation
#
max_nr_of_steps = 10  # Maximum number of steps simulation is allowed to run


# --------
# Display
#
print_boat_data = True
print_boat_belief = True
print_env_data = True
plot_crossings = False


# --------
# Boats
#
nr_of_boats = 1


# --------
# Error
#
location_error = 0
heading_error = 0
course_marker_error = 0.05
boom_measure_error = utilsmath.rad(5)
boom_control_error = utilsmath.rad(5)
rudder_measure_error = utilsmath.rad(5)
rudder_control_error = utilsmath.rad(5)


# --------
# Environment
#
# Wind
wind_prevailing = None  # Set to None for random prevailing wind. Otherwise set to tuple (speed, angle)
wind_max = 20  # Maximum wind speed in mph
wind_min = 5  # Minimum wind speed in mpg
wind_speed_sigma = 2.0  # Standard deviation for wind speed
wind_direction_sigma = 3.14 / 8.0  # Standard deviation for wind direction
wind_change_rate = 3  # Nr of time steps. Wind change will be spread across this many time steps.
#
# Course
course_range = 100
num_landmarks = 5
num_course_marks = 5
