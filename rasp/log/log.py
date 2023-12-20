from datetime import datetime
import classes.state as state
from classes.tools import get_current_date
import logging
logging.basicConfig(filename="log/log.txt", level=logging.DEBUG, format="%(message)s")

def log_start(name:str = "default"):
    logging.debug(msg=datetime.now().strftime("%d %B %Y %H:%M:%S"))
    log_config(name)
    
def log_config(name:str = "default"):
    if name == "main":
        logging.debug
        (
            f"test : {state.test}"
            f"check_collisions : {state.check_collisions}"
            f"time_to_return_to_home : {state.time_to_return_to_home}s"
        )

def log_call(name : str):
    def decorator(func):
        if(state.activate_log):
            def wrapper(*args,**kwargs):
                header = f"{round(get_current_date()["date_timespamp"]-state.start_time,2)} : rasp -> {name} : {func.__name__}("
                # get positional parameters
                params = [f"{param}={value}"for param, value in zip(func.__code__.co_varnames,args)]
                # get keyword parmeters
                params += [f"{key}={value},"for key,value in kwargs.items()]
                for e in params:
                    header+=e[:-1]+", "
                header=header[:-2]+")"
                logging.debug(msg="\t"+header)
                return func(*args,**kwargs)
            return wrapper
        return func
    return decorator
    
def log_rcv(name : str, action_finished_message : dict[bytes,str]):
    def decorator(func):
        if(state.activate_log):
            def wrapper(*args, **kwargs):
                header = f"{round(get_current_date()["date_timespamp"]-state.start_time,2)} : rolling_basis -> {name} : {action_finished_message.get(args[0],"unknown")}"
                logging.debug("\t"+header)
                return func(*args,**kwargs)
            return wrapper
        return func
    return decorator