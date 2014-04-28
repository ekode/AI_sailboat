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
            if sim_config.print_boat_belief:
                print 'bel. position', boat_agents[b_id].believed_location
                print 'bel. velocity', boat_agents[b_id].believed_velocity
            if sim_config.print_boat_data:
                print 'heading', env.boats[b_id].heading
                print 'wind angle', env.boats[b_id].relative_wind_angle
                print 'speed', env.boats[b_id].speed
    pass


def start():
    print ' '
    print 'Starting simulation'

    pass


def end():
    print ' '
    print 'Finished simulation'