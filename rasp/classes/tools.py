import classes.state as state
from classes.constants import *
from datetime import datetime
from environment.geometric_shapes.oriented_point import OrientedPoint as op
# use lidarTools.py in order to develop functions using the lidar. In enables to test and use those one without having access to it

def get_current_date():
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

def get_polar_points(self):
    return self.__scan_values_to_polar()