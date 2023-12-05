from classes.lidar import Lidar
import math

# Get Lidar
lidar = Lidar(-math.pi, math.pi)

print(f"is_obstacle : {lidar.is_obstacle_infront()}")