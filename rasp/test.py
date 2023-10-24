from classes.lidar import Lidar
import Libraries.Teensy_Com as teensy
from classes.point import point as p
import math

# Get Lidar
lidar = Lidar(-math.pi, math.pi)

print(f"is_obstacle : {lidar.is_obstacle_infront()}")
rolling_basis = teensy.Rolling_basis(crc=None)
point = p(10,0)
print(f"going to : {point.__str__()}")
rolling_basis.Go_To(point)