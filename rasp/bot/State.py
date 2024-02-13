from queue import Queue

################
#     INIT     #
################
# set to 0 to avoid errors
start_time = 0


################
#    STATE     #
################
# do not set to False
is_moving = True

# for safety in case of lidar dysfunction
is_obstacle = True

# for safety in case of lidar dysfunction
run_auth = False

# A list of tuples representing the points to be reached and the according action to execute once reached
points_list = []

# the index of the last point
index_last_point = len(points_list) - 1

# index of our destination point
index_destination_point = 0

game_finished = False



################
#    CONFIG    #
################
# 0: INFO, 1: WARNING, 2: ERROR, 3: CRITICAL, 4: NONE
LOG_LEVEL = 0
PRINT_LOG = True
is_logger_init = False

go_to_verif = True # when true trajectory is checked to avoid forbidden moves
activate_lidar = True # when true stops when an obstacle is detected


plant_time = 0
solar_panel_time = 5
time_to_return_home = 10


SERVOS_PIN = [5] # the maxmimun number of servos is 12
ULTRASONICS_PINS = [(12,14)]

test = False
activate_print = True