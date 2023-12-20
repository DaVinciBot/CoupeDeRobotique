import classes.state as state
from classes.constants import *
from datetime import datetime
from environment.geometric_shapes.oriented_point import OrientedPoint as op
from environment.arenas.mars_arena import MarsArena
# use lidarTools.py in order to develop functions using the lidar. In enables to test and use those one without having access to it

def get_current_date():
    now = datetime.now()
    timestamp = datetime.timestamp(now)
    return {
        "date": now,
        "date_timespamp": timestamp
    }
    
def add_op(oriented_point : op)->bool:  # op stands for oriented point
    if state.check_collisions:
        if MarsArena.enable_go_to(state.points_list[-1],oriented_point):
            state.points_list.append(oriented_point)
            state.index_last_point += 1
            return True
        return False
    else:
        state.points_list.append(oriented_point)
        state.index_last_point += 1
        return True

def select_action_at_position(zone : int):
    if zone == CMD_POTAREA:
        print("taking plant")
    elif zone == CMD_DEPOTZONE:
        print("deposing plant into depot zone")
    elif zone == CMD_GARDENER:
        print("deposing plant into gardener")
    else:
        print(f"zone {zone} isn't take in cahrge")





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