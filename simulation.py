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
import plot
import argparse

parser = argparse.ArgumentParser(description='Graph environment test')
parser.add_argument('--crossings', action='store_true', help='Plot marker crossings')
args = parser.parse_args()

env = environment.environment()
polar_plot = plot.plot()
polar_plot.start()
polar_plot.plot_course(env, polar_plot)
polar_plot.show()
#env.plot()

#env.plot(args.crossings)


# Plot arrow at the origin for the initial wind
polar_plot.arrow((0, 0), env.current_wind, 'blue')

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

        polar_plot.true_boat(env.boats[boat_agent.boat_id].location)
        polar_plot.boat_belief(boat_agents[boat_agent.boat_id].believed_location)
        polar_plot.boat_measured(boat_agents[boat_agent.boat_id].measured_location)
        polar_plot.draw()

        if i == 0:
            boat_agent.plot_plan(polar_plot)
            pass

    report.report(env, boat_agents, i)

    # Update Environment and change wind conditions for the next time step
    env.update(all_boats_controls)
    env.change_wind(i)
    i += 1

report.end()
polar_plot.end()
polar_plot.show()
