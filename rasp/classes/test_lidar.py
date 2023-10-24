from lidar import Lidar
import math

# Get Lidar
lidar = Lidar(-math.pi, math.pi)

print(lidar.is_obstacle_infront())