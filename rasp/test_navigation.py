from classes.lidar import Lidar
import Libraries.Teensy_Com as teensy
from classes.point import point
import math
import time

# Get Lidar
lidar = Lidar(-math.pi, math.pi)
rolling_basis = teensy.Rolling_basis(crc=False)
points_list = [(point(10,0),0), (point(0,10),1)]
index_destination_point : int = 0
rolling_basis.Go_To(points_list[index_destination_point][0])
time.sleep(10)
index_destination_point += 1
rolling_basis.Go_To(points_list[index_destination_point][0])


