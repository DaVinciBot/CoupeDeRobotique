import lidar
import math

lidar = lidar.Lidar(-math.pi, math.pi)
print(lidar.safe_get_nearest_point_between(90,180,1/3))