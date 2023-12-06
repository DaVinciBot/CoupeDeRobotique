from classes.lidar import Lidar
from classes.tools import *
import Libraries.Teensy_Com as teensy
import math
import time

# Get Lidar
lidar = Lidar(-math.pi, math.pi)

print(f"Direction possible : {get_possible_directions(lidar)}")
input("enter to continue")
print(f"Direction possible : {get_possible_directions(lidar)}")
input("enter to continue")
print(f"Direction possible : {get_possible_directions(lidar)}")
input("enter to continue")
print(f"Direction possible : {get_possible_directions(lidar)}")
input("enter to continue")
print(f"Direction possible : {get_possible_directions(lidar)}")
input("enter to continue")

