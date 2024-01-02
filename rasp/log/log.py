from datetime import datetime
import classes.state as state
from classes.tools import get_current_date
from classes.constants import *
import logging

logging.basicConfig(filename="log/log.txt", level=logging.DEBUG, format="%(message)s")

def log_start():
    logging.debug(msg=datetime.now().strftime("%d %B %Y %H:%M:%S"))
    if state.activate_com_log :
        log_rolling_basis_config()
        log_actuator_config()
        
def log_rolling_basis_config():
    logging.debug
    (
        f"ROLLING BASIS CONFIG"
        f"test : {state.test}"
        f"check_collisions : {state.check_collisions}"
        f"time_to_return_to_home : {state.time_to_return_to_home}s"
    )
    
def log_actuator_config():
    logging.debug
    (
        f"ACTUATORS CONFIG"
        f" servo motors' pin : {SERVOS_PIN}"
    )

def log_call(name : str):
    def decorator(func):
        if state.activate_com_log:
            def wrapper(*args,**kwargs):
                header = f"{round(get_current_date()["date_timespamp"]-state.start_time,2)} : rasp -> {name} : {func.__name__}("
                # get positional parameters
                params = [f"{param}={value}"for param, value in zip(func.__code__.co_varnames,args)]
                # get keyword parmeters
                params += [f"{key}={value},"for key,value in kwargs.items()]
                for e in params:
                    header+=e[:-1]+"),"
                header=header[:-2]+"))"
                logging.debug(msg="\t"+header)
                return func(*args,**kwargs)
            return wrapper
        return func
    return decorator

def log_rcv(name : str, action_finished_message : dict[bytes,str]):
    def decorator(func):
        if state.activate_com_log:
            def wrapper(*args, **kwargs):
                header = f"{round(get_current_date()["date_timespamp"]-state.start_time,2)} : rolling_basis -> {name} : {action_finished_message.get(args[0],"unknown")}"
                logging.debug("\t"+header)
                return func(*args,**kwargs)
            return wrapper
        return func
    return decorator

def log_function(func):
    if state.activate_decision_process_log:
        def wrapper(*args,**kwargs):
            header = f"{round(get_current_date()["date_timespamp"]-state.start_time,2)} : {func.__name__}("
            # get positional parameters
            params = [f"{param}={value}"for param, value in zip(func.__code__.co_varnames,args)]
            # get keyword parmeters
            params += [f"{key}={value},"for key,value in kwargs.items()]
            for e in params:
                header+=e[:-1]+", "
            header=header[:-2]+")) -> "
            result = func(*args,**kwargs)
            try : prompt = str(result)
            except : prompt = "..."
            logging.debug(msg="\t"+header+prompt)
        return wrapper
    return func
    
