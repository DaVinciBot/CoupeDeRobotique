# Used to represent the possible directions of the robot
ERROR :int = -1
STRAIGHT :int = 0
LEFT :int = 1
RIGHT :int = 2
BOTH :int = 3 # represents that both right and left are possible

# Commands to execute at the specified area
CMD_POTAREA :int = 0
CMD_DEPOTZONE :int = 1
CMD_GARDENER :int = 2

# Actuators
SERVO1_PIN :int = 5 # pins must correspond to the one defined on the teensy
SERVOS_PIN = [SERVO1_PIN]