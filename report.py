#
# Utility functions for reporting environment and boat statuses
#
# Authors: Jonathan Hudgins <jhudgins8@gatech.edu>, Igor Negovetic <igorilla@gmail.com>
#

import sim_config

def report(env, boat_agents, i):
    print ' '
    print '---step', i, '---'

    # Printing environment and boats data
    if sim_config.print_wind_change:
        print ' '
        print 'new goal wind', env.goal_wind
        print 'wind change', (env.wind_speed_change, env.wind_direction_change)
    if sim_config.print_env_data:
        print ' '
        print 'wind', env.current_wind
    if sim_config.print_boat_data or sim_config.print_boat_belief:
        for b_id in range(sim_config.nr_of_boats):
            print ' '
            print 'boat', b_id
            if sim_config.print_boat_data:
                print 'real position', env.boats[b_id].location
                print 'real speed', env.boats[b_id].speed
                print 'real heading', env.boats[b_id].heading
                print 'wind angle', env.boats[b_id].relative_wind_angle
                print 'rudder', env.boats[b_id].rudder
            if sim_config.print_boat_belief:
                print ' '
                print 'bel. position', boat_agents[b_id].believed_location
                print 'bel. speed', boat_agents[b_id].believed_speed
                print 'bel. heading', boat_agents[b_id].believed_heading
                print 'meas heading', boat_agents[b_id].measured_heading

    print '---end step---'


def start():
    print ' '
    print 'Starting simulation'


def end():
    print ' '
    print 'Finished simulation'