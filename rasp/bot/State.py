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

# enable to manage actions once a given position is reached
actions_at : list[function]= []

# index of our destination point
index_destination_point = 0

game_finished = False

# enable to give a unique id to each GoTo
id_current_GoTo = 0 

# usefull to lauch actions once the previous finished
action_selector = 0

################
#    CONFIG    #
################
# 0: INFO, 1: WARNING, 2: ERROR, 3: CRITICAL, 4: NONE
LOG_LEVEL = 0
PRINT_LOG = True
is_logger_init = False

go_to_verif = False # when true trajectory is checked to avoid forbidden moves
activate_lidar = True # when true stops when an obstacle is detected

time_to_return_home = 80


SERVOS_PIN = [5] # the maxmimun number of servos is 12
ULTRASONICS_PINS = [(12,14)]



test = False
activate_print = True