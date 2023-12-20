import math
from classes.lidar import lidar

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

def get_possible_directions(self, start_angle = 90, end_angle = 180, step_angle = 1/3, treshold = 0.2, delay_mili = 10) -> int:
        """NOT OPERATIONAL YET : a basic function that enable to analyse the moving direction of an obstacle and return the possible directions for us 

        Args:
            start_angle (int, optional): the first angle taken into account in the process. Defaults to 0.
            end_angle (_type_, optional): the last angle taken into account in the process. Defaults to len(lidar.scan.distances).
            step_angle (_type_, optional): enable to compute indexs of the given angles in the tab. Defaults to 1/3.
            treshold (float, optional): if the distance between the robot and an element is under tresholde then consider it as an obstacle. Defaults to 0.2.
            delay_mili (int, optional): the delay between the two mesure of the lidar. Defaults to 10.

        Returns:
            int: _description_
        """
        try:
            i_min : int = int(start_angle/step_angle)
            i_max : int = int(end_angle/step_angle)
            i : int = i_min
            lidar.scan()
            first_start : int = -1 # must be set to -1
            while(i<i_max and first_start == -1): # get the index of the first distance under treshold
                if(lidar.scan.distances[i]<=treshold):
                    first_start = i
                else : i+=1
            if first_start == -1: # no distance under treshold
                return constants.STRAIGHT
            i=i_max
            first_stop : int = -1
            while(i>-1 and first_stop == -1): # get the index of the last distance under treshold
                if(lidar.scan.distances[i]<=treshold):
                    first_stop = i
                else : i-=1
            time.sleep(delay_mili/1000) # we wait a little bit before the second mesure
            lidar.scan()
            i=0
            second_start : int = -1
            while(i<i_max and second_start == -1): # get the index of the first distance under treshold
                if(lidar.scan.distances[i]<=treshold):
                    second_start = i
                else : i+=1
            if second_start == -1: # no longer any distance under treshold
                return constants.STRAIGHT
            i=i_max
            second_stop : int = -1
            while(i>-1 and second_stop == -1): # get the index of the last distance under treshold
                if(lidar.scan.distances[i]<=treshold):
                    second_stop = i
                else : i-=1
            if second_start < first_start and second_stop < first_stop : # is the other robot going left ?
                return constants.RIGHT
            if second_start > first_start and second_stop > first_stop : # is the other robot going right ?
                return constants.LEFT
            return constants.ERROR

        except :
            return constants.ERROR