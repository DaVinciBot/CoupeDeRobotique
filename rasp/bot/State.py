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

# Pins of the servos (int), the maximum of pin is 12
SERVOS_PIN = []

test = False
activate_print = True