#from classes.intercom_tools import intercom, send_coords, update_target_point
from classes.tools import get_current_date
from classes.lidar import Lidar
from classes.pinInteract import PIN
from classes.constants import *
from environment.arenas.mars_arena import MarsArena
from environment.geometric_shapes.oriented_point import OrientedPoint as op
import Libraries.Teensy_Com as teensy
import math
import time

test = True

# Get Lidar
lidar = Lidar(-math.pi, math.pi)

# Print variables
last_print = get_current_date()["date_timespamp"]

# Return to start timing
start_time = 0
time_to_return_to_home = 80

# Get arena
arena : MarsArena = MarsArena()

# Get Rolling_basis
rolling_basis = teensy.Rolling_basis(crc=True)

if(test):
    rolling_basis.Set_Home()
    print(rolling_basis.odometrie)
    time.sleep(0.01)
    # temporary
    rolling_basis.action_finished = False
    

def select_action_at_position(zone : int):
    if zone == CMD_POTAREA:
        print("taking plant")
    elif zone == CMD_DEPOTZONE:
        print("deposing plant into depot zone")
    elif zone == CMD_GARDENER:
        print("deposing plant into gardener")
    else:
        print(f"zone {zone} isn't take in cahrge")

# A list of tuples representing the points to be reached and the according action to execute once reached
points_list = [(op(5,0),CMD_POTAREA), (op(0,5),CMD_DEPOTZONE)]
# index of our destination point
index_destination_point : int = 0
index_last_point : int = len(points_list)-1
# enable to say if the robot habe been previously stopped
have_been_stopped = True
is_obstacle : bool = True # for safety in case of lidar dysfunction

while True:
    is_obstacle : bool = True # for safety in case of lidar dysfunction
    game_finished = False
    while(index_destination_point<index_last_point+1 and not game_finished): # while there are points left to go through and time is under treshold 
        # is_there an obstacle in front of the robot ? 
        # Run authorize ?
        try:
            is_obstacle = lidar.is_obstacle_infront()
        except Exception as e:
            print("oo")
            print(e)
        run_auth : bool = not is_obstacle
        # Go to the next point. If an obstacle is detected stop the robot
        if not run_auth:
            rolling_basis.Keep_Current_Position()
            rolling_basis.action_finished = False
            have_been_stopped = True
        elif have_been_stopped:
            rolling_basis.Go_To(points_list[index_destination_point][0])
            have_been_stopped = False

        if rolling_basis.action_finished:
            print(f"arrived at {points_list[index_destination_point][0]}")
            index_destination_point += 1
            have_been_stopped = True
            rolling_basis.action_finished = False # not necessary but for safety 

        # Check if there is enought time
        #if tirette_pin.digitalRead() and start_time == 0:
            #start_time = get_current_date()["date_timespamp"]

        # if time exceeds time_to_return_home then go to the starting posistion
        if start_time !=0 and get_current_date()["date_timespamp"] - start_time > time_to_return_to_home:
            game_finished = True

        # A print every 500 ms
        if (get_current_date()["date_timespamp"] - last_print) > 0.5:
            last_print = get_current_date()["date_timespamp"]

            """print(f"#-- Lidar --#\n"
                f"is_obstacle: {is_obstacle}\n\n"
                f"#-- Pins --#\n"
                #f"State Tirette: {tirette_pin.digitalRead()}\n"
                f"#-- Timer (return to home) --#\n"
                f"Timer to return: {time_to_return_to_home}\n"
                f"Current time: {round(get_current_date()['date_timespamp'] - start_time)}\n"
                f"#-- Run --#\n"
                f"Auth state: {run_auth}\n")"""
        
        #rolling_basis.Go_To(arena.home.center)

