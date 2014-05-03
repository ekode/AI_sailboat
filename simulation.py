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

env = environment.environment()
polar_plot = plot.plot()
polar_plot.start()
polar_plot.plot_course(env, polar_plot)
polar_plot.show()
#env.plot()

# Plot arrow at the origin for the initial wind
polar_plot.arrow((0, 0), env.current_wind, 'blue')

boat_agents = []
for i in range(sim_config.nr_of_boats):
    boat_agents.append(sailboat_control.sailboat_control(env))

report.start()

i = 0
while not env.is_finished(i):
    all_boats_controls = []
    for boat_id in range(len(env.boats)):
        (boom_angle, rudder_angle) = boat_agents[boat_id].boat_action()
        all_boats_controls.append((boom_angle, rudder_angle))

        polar_plot.true_boat(env.boats[boat_id].location)
        polar_plot.boat_belief(boat_agents[boat_id].believed_location)
        polar_plot.boat_measured(boat_agents[boat_id].measured_location)
        polar_plot.draw()
        #polar_plot.show()

    report.report(env, boat_agents, i)

    # Update Environment and change wind conditions for the next time step
    env.update(all_boats_controls)
    env.change_wind(i)
    i += 1

report.end()
polar_plot.end()
polar_plot.show()