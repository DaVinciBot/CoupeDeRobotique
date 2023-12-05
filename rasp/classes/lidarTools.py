import math

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