from classes import lidar
import time
from classes import constants
from classes.lidar import Lidar

def get_current_date():
    from datetime import datetime
    now = datetime.now()
    timestamp = datetime.timestamp(now)
    return {
        "date": now,
        "date_timespamp": timestamp
    }

def is_list_of(list : list, type)->bool:
    """tell wether the list contains only element of the given type

    Args:
        list (list): the list to test
        type (_type_): an object with requiered type

    Returns:
        bool: true if all the elements of list are elements of the given type
    """
    test = True
    n = 0
    while test and n<list.count():
        if not isinstance(list[n],type(type)):
            test = False
        n+=1
    return test

def get_possible_directions(lidar : Lidar, start_angle = 90, end_angle = 180, step_angle = 1/3, treshold = 0.2, delay_mili = 10) -> int:
    """a basic function that enable to analyse the moving direction of an obstacle and return the possible directions for us 

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