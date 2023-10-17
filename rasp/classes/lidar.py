import math
import pysicktim as lidar


def scan_values_to_polar(scan_values, min_angle, max_angle):
    """permet de 

    Args:
        scan_values (_type_): _description_
        min_angle (_type_): _description_
        max_angle (_type_): _description_

    Returns:
        _type_: _description_
    """
    angle_step = (max_angle - min_angle) / len(scan_values)
    polar_coordinates = []
    for i in range(len(scan_values)):
        polar_coordinates.append(
            (min_angle + i * (angle_step), scan_values[i]))
    return polar_coordinates


def polar_to_cartesian(polar_coordinates):
    cartesian_coordinates = []

    for coordinate in polar_coordinates:
        cartesian_coordinates.append(
            (coordinate[1] * math.cos(coordinate[0]), coordinate[1] * math.sin(coordinate[0])))

    return cartesian_coordinates


def threshold(polar_coordinates, threshold):
    res = []
    for coordinate in polar_coordinates:
        if (coordinate[1] < threshold):
            res.append(coordinate)
    return res


# robot_pos=(x,y,theta), theta is the way the robot is turned
def relative_to_absolute_cartesian_coordinates(cartesian_coordinates, robot_pos):
    res = []
    for coordinate in cartesian_coordinates:
        res.append((robot_pos[0]+coordinate[0]*math.cos(robot_pos[2]),
                   robot_pos[1]+coordinate[1]*math.sin(robot_pos[2])))
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

    def get_nearest_point(self, start ):
        lidar.scan()
        points = [val for val in lidar.scan.distances if val > 0.01]
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
    
    def safe_get_nearest_point_between(self,start_angle, end_angle, step_angle):
        """give the nearest point between the requiered angles 

        Args:
            start_angle (float): the angle from were to start mesuring
            end_angle (float): the last angle of the mesure 
            step_angle (float): every mesusre from the lidar is separeted from a given angle

        Returns:
            _type_: _description_
        """
        points = []

        for _ in range(30):
            lidar.scan()
            # start_angle/step_angle give us the index of the point at start angle in the lidar.scan.distances array
            scan = [lidar.scan.distances[i] for i in range(int(start_angle/step_angle), int(end_angle/step_angle)) if lidar.scan.distances[i] > 0.01]
            scan.sort()
            points.append(scan[0])

        points.sort()
        return points[len(points) // 2]
    
    def is_obstacle_infront(self, robot_pos, start_angle = 90, end_angle = 180, step_angle = 1/3, treshold=0.2):
        """this function enable to detect an obstacle in front of the robot. Do not exclude objects outside the bord. Therefore treshold must be low to avoid stopping for nothing

        Args:
            robot_pos (_type_): the actual position of the robot gieven by (x,y,theta), theta is the way the robot is turned
            start_angle (int, optional): the angle from were to start measuring. Defaults to 90 because of the actual position of the lidar
            end_angle (int, optional): the angle from were to stop mesuring. Defaults to 180 beacause of the actual position of the lidar
            step_angle (_type_, optional): _description_. Defaults to 1/3 because of the acual lidar configuration
            treshold (float, optional): _description_. Defaults to 0.2. Must be low to avoid detecting objects outside of the board
        """
        nearest_point = self.safe_get_nearest_point_between(self, start_angle, end_angle, step_angle, treshold)
        if(nearest_point<=treshold): return True
        else : return False
            
        
    def get_cartesian_points(self):
        return self.__polar_to_cartesian()
    

    def get_polar_points(self):
        return self.__scan_values_to_polar()
