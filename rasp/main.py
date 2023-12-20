import math
import time
from log.log import log_start
from classes.tools import *
from classes.lidar import Lidar
from classes.pinInteract import PIN
from classes.constants import *
import classes.state as state
from environment.arenas.mars_arena import MarsArena
from environment.geometric_shapes.oriented_point import OrientedPoint as op
import Libraries.Teensy_Com as teensy



lidar = Lidar(-math.pi, math.pi)
arena : MarsArena = MarsArena()
rolling_basis = teensy.Rolling_basis(crc=True)

last_print = get_current_date()["date_timespamp"]

if state.test:
    rolling_basis.Set_Home()
    print(rolling_basis.odometrie)
    time.sleep(0.01)
    
state.start_time = get_current_date()["date_timespamp"]
if state.activate_log:
    log_start("main")
    
while True:
    while(state.index_destination_point<state.index_last_point+1 and not state.game_finished): # while there are points left to go through and time is under treshold 
        # is_there an obstacle in front of the robot ? 
        # Run authorize ?
        try:
            state.is_obstacle = lidar.is_obstacle_infront()
        except Exception as e:
            print(e)
        state.run_auth : bool = not state.is_obstacle
        
        if state.test:
            print(f"action_finished : {rolling_basis.action_finished}")

        # Go to the next point. If an obstacle is detected stop the robot
        if not state.run_auth:
            if state.is_moving :
                rolling_basis.Keep_Current_Position()
                state.is_moving = False
        if state.run_auth and not state.is_moving:
            rolling_basis.Go_To(state.points_list[state.index_destination_point][0])
            state.is_moving = True
        if rolling_basis.action_finished:
            print(f"arrived at {state.points_list[state.index_destination_point][0]}")
            state.index_destination_point += 1
            state.is_moving = False

        # if time exceeds time_to_return_home then go to the starting posistion
        if state.start_time !=0 and get_current_date()["date_timespamp"] - state.start_time > state.time_to_return_to_home:
            if not state.test:
                rolling_basis.Go_To(arena.home.center)

        # A print every 500 ms if activated
        if state.activate_print and (get_current_date()["date_timespamp"] - last_print) > 0.5:
            last_print = get_current_date()["date_timespamp"]

            print
            (
                f"#-- Lidar --#\n"
                f"is_obstacle: {state.is_obstacle}\n\n"
                f"#-- Pins --#\n"
                #f"State Tirette: {tirette_pin.digitalRead()}\n"
                f"#-- Timer (return to home) --#\n"
                f"Timer to return: {state.time_to_return_to_home}\n"
                f"Current time: {round(get_current_date()['date_timespamp'] - state.start_time)}\n"
                f"#-- Run --#\n"
                f"Auth state: {state.run_auth}\n"
            )

