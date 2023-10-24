from lidar import Lidar
from rasp.Libraries.Teensy_Com import Teensy as teensy
from classes.point import point as p
import math

# Get Lidar
lidar = Lidar(-math.pi, math.pi)

print(f"is_obstacle : {lidar.is_obstacle_infront()}")
rolling_basis = teensy.Rolling_basis(crc=False)
point = p(10,0)
print(f"going to : {point.__str__()}")
rolling_basis.Go_To(point)