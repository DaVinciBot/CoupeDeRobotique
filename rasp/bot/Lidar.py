import math
import pysicktim as lidar


def scan_values_to_polar(scan_values, min_angle, max_angle):
    angle_step = (max_angle - min_angle)/ len(scan_values)
    polar_coordinates = []
    for i in range(len(scan_values)):
        polar_coordinates.append((min_angle + i *(angle_step),scan_values[i]))
    return polar_coordinates


def polar_to_cartesian(polar_coordinates):
    cartesian_coordinates = []

    for coordinate in polar_coordinates:
        cartesian_coordinates.append((coordinate[1] * math.cos(coordinate[0]), coordinate[1] * math.sin(coordinate[0])))

    return cartesian_coordinates

def threshold(polar_coordinates, threshold):
    res = []
    for coordinate in polar_coordinates:
        if (coordinate[1] < threshold): res.append(coordinate)
    return res

def relative_to_absolute_cartesian_coordinates(cartesian_coordinates,robot_pos): ## robot_pos=(x,y,theta), theta is the way the robot is turned
    res = []
    for coordinate in cartesian_coordinates:
        res.append((robot_pos[0]+coordinate[0]*math.cos(robot_pos[2]),robot_pos[1]+coordinate[1]*math.sin(robot_pos[2])))
    return res

def is_under_threshold(polar_coordinates, threshold):
    return (min([x[1] for x in polar_coordinates]) < threshold)

class Lidar:
    def __init__(self, min_angle, max_angle):
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.lidar_obj = lidar

    def __scan(self):
        self.lidar_obj.scan()

    def __scan_values(self):
        return self.lidar_obj.scan.distances

    def __scan_values_to_polar(self):
        return scan_values_to_polar(self.__scan_values(), self.min_angle, self.max_angle)

    def __polar_to_cartesian(self):
        return polar_to_cartesian(self.__scan_values_to_polar())

    def get_nearest_point(self):
        lidar.scan()
        points = [val for val in lidar.scan.distances if val > 0.01]
        points.sort()
        return points[0]

    def get_face_nearest_point(self):
        lidar.scan()
        points = [val for val in lidar.scan.distances[269:-271] if val > 0.01]
        points.sort()
        return points[0]

    def safe_get_nearest_point(self):
        points = []
        for _ in range(30):
            lidar.scan()
            scan = [val for val in lidar.scan.distances if val > 0.01]
            scan.sort()
            points.append(scan[0])
            
        points.sort()
        return points[len(points) // 2]

    def safe_face_get_nearest_point(self):
            points = []
            for _ in range(30):
                points.append(self.get_face_nearest_point())
                
            points.sort()
            return points[len(points) // 2]

    def get_cartesian_points(self):
        return self.__polar_to_cartesian()

    def get_polar_points(self):
        return self.__scan_values_to_polar()