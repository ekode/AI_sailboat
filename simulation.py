#
# Sailboat Simulation
#
# Main file that performs the simulation.
#
# Authors: Jonathan Hudgins <jhudgins8@gatech.edu>, Igor Negovetic <igorilla@gmail.com>
#

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
How this works:

simulation
    creates environment (instance of environment class)
    creates boat_agents (instances of sailboat_control class)
        each boat_agent calls env.create_boat() to create true_sailboat representation of itself
    loop
        for each boat
            boat_agent performs action by adjusting boat controls
            environment updates
                true_sailboat calculates velocity vector
        change wind speed and direction

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

import sim_config
import environment
import sailboat_control

env = environment.environment()
env.plot()

# Plot arrow at the origin for the initial wind
env.plotter.arrow((0, 0), (env.current_wind[1], env.current_wind[0]), 'blue')

boat_agents = []
for i in range(sim_config.nr_of_boats):
    boat_agents.append(sailboat_control.sailboat_control(env))


print ' '
print 'Starting simulation'

# for now just loop 10 times
# while True:
for i in range(10):
    print ' '
    print '---step', i, '---'

    all_boats_controls = []
    for boat_id in range(len(env.boats)):
        (boom_angle, rudder_angle) = boat_agents[boat_id].boat_action()
        all_boats_controls.append((boom_angle, rudder_angle))

    env.update(all_boats_controls)

    env.change_wind()

print ' '
print 'Finished simulation'
env.plotter.show()
