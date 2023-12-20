from environment.geometric_shapes.oriented_point import OrientedPoint as op
from classes.constants import *

start_time = 0 # set to 0 to avoid errors

# *OPTIONS*
activate_log : bool = True # enable or disable logging's functionnalities
test = True
activate_print : bool = True
check_collisions : bool = False
index_destination_point : int = 0 # index of our destination point

# *STATE*
game_finished : bool = False
is_moving : bool = True # do not set to False
is_obstacle : bool = True # for safety in case of lidar dysfunction
run_auth : bool = False # for safety in case of lidar dysfunction
points_list : list[(op,int)] = [(op(5,0),CMD_POTAREA), (op(0,5),CMD_DEPOTZONE)] # A list of tuples representing the points to be reached and the according action to execute once reached
index_last_point : int = len(points_list)-1 # the index of the last point

# *STRAT*
time_to_return_to_home = 80 # return to home timing