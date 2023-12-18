import classes.data as data
from datetime import datetime
# use lidarTools.py in order to develop functions using the lidar. In enables to test and use those one without having access to it


def save_registered_actions(file_name = "rasp/register/reports.txt"):
    with open(file_name, 'a') as fichier:
        now = datetime.now().strftime("%d %B %Y %H:%M:%S")
        fichier.write(now+"\n")
        for ligne in data.registered_actions:
            fichier.write("\t"+ligne + "\n")

def register_call(name : str):
    def decorator(func):
        def wrapper(*args,**kwargs):
            header = f"{get_current_date()["date_timespamp"]-data.start_time} : rasp -> {name} : {func.__name__}"
            params = [f"{param}={value}"for param, value in zip(func.__code__.co_varnames,args)]
            params += [f"{key}={value}"for key,value in kwargs.items()]
            data.registered_actions += [f"{header}({','.join(params)})"]
            return func(*args,**kwargs)
        return wrapper
    return decorator
    
def register_rcv(name : str, action_finished_message : dict[bytes,str]):
    def decorator(func):
        def wrapper(*args, **kwargs):
            header = f"{get_current_date()["date_timespamp"]-data.start_time} : rolling_basis -> {name} : {action_finished_message.get(args[0],"unknown")}"
            data.registered_actions += [header]
            return func(*args,**kwargs)
        return wrapper
    return decorator

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


def is_in_tab(array, val)->bool:
    """tell wether val is in array

    Args:
        array (_type_): the array to look in
        val (_type_): the value to search for

    Returns:
        bool: true if val is in array, false otherwise
    """
    def is_in(debut, fin):
        if debut > fin:
            return False
        middle = (debut + fin) // 2
        if array[middle] == val:
            return True
        elif array[middle] > val:
            return is_in(array, debut, middle - 1, val)
        else:
            return is_in(array, middle + 1, fin, val)
    return is_in(0, len(array) - 1)

def get_polar_points(self):
    return self.__scan_values_to_polar()