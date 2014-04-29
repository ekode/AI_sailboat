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
            boat_agent is asked what change in controls it wants to make
                boat_agent localizes
                boat_agent plans
                boat_agent provides control adjustments

        environment updates
            for each true_sailboat
                true_sailboat calculates velocity vector
                true_sailboat calculates new position
        change wind speed and direction

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

import sim_config
import environment
import sailboat_control
import report
import argparse

parser = argparse.ArgumentParser(description='Graph environment test')
parser.add_argument('--crossings', action='store_true', help='Plot marker crossings')
args = parser.parse_args()

env = environment.environment()
env.plot(args.crossings)

# Plot arrow at the origin for the initial wind
env.plotter.arrow((0, 0), env.current_wind, 'blue')

boat_agents = []
for i in range(sim_config.nr_of_boats):
    boat_agents.append(sailboat_control.sailboat_control(env))

report.start()

i = 0
while not env.is_finished(i):
    all_boats_controls = []
    for boat_agent in boat_agents:
        (boom_angle, rudder_angle) = boat_agent.boat_action()
        all_boats_controls.append((boom_angle, rudder_angle))

        env.plotter.boat_belief(boat_agent.believed_location)

        if i == 0:
            boat_agent.plot_plan()

    report.report(env, boat_agents, i)

    # Update Environment and change wind conditions for the next time step
    env.update(all_boats_controls)
    env.change_wind(i)
    i += 1

report.end()
env.plotter.show()



