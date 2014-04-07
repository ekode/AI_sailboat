import environment
import sailboat_control

env = environment.environment()
boat_control = sailboat_control.sailboat_control(env)

# for now just loop 10 times
# while True:
for i in range(10):
    boat_control.boat_id
    (boom_adjust, rudder_adjust) = boat_control.boat_action()
    env.update()
