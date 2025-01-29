# ====== Code Summary ======
# This module provides logging and time-tracking decorators to enhance function/method monitoring.

# ====== Imports ======
# Standard library imports
from typing import Callable
from functools import wraps
import inspect
import time

# Internal project imports
from logger.logger import Logger
from logger.log_levels import LogLevels


# ====== Tools functions ======
def get_function_metadata(func: Callable, args, kwargs) -> str:
    """
    Generate a concise string containing function/method metadata, including module, class (if applicable), 
    function name, and parameter values.

    Args:
        func (Callable): The function being described.
        args (tuple): Positional arguments passed to the function.
        kwargs (dict): Keyword arguments passed to the function.

    Returns:
        str: A formatted string containing function metadata.
    """
    frame = inspect.currentframe().f_back.f_back
    module_name = frame.f_globals["__name__"].split(".")[-1]  # Shortened module name
    class_name = args[0].__class__.__name__ if args and hasattr(args[0], "__class__") else None

    # Retrieve parameter names and values
    bound_args = inspect.signature(func).bind(*args, **kwargs)
    bound_args.apply_defaults()
    params_info = ", ".join(f"{k}={v!r}" for k, v in bound_args.arguments.items())

    return f"[{module_name}] {class_name + '.' if class_name else ''}{func.__name__}({params_info})"


def get_logger_from_decorator_param(param_logger: Logger | str | Callable, args) -> Logger | None:
    """
    Retrieve a Logger instance from various possible inputs: an existing Logger, a string identifier, or 
    a callable that returns a logger.

    Args:
        param_logger (Logger | str | Callable): The logger parameter passed to the decorator.
        args (tuple): Positional arguments passed to the decorated function.

    Returns:
        Logger | None: A Logger instance if successfully resolved, otherwise None.
    """
    if isinstance(param_logger, Logger):
        return param_logger
    if isinstance(param_logger, str):
        return Logger(identifier=param_logger)
    if param_logger is not None:
        instance = args[0]  # First argument of a bound method is typically `self`
        return param_logger(instance)
    return None


# ====== Decorators ======
def time_tracker(param_logger: Logger | str | Callable = None):
    """
    Decorator to measure and log the execution time of a function/method.

    Args:
        param_logger (Logger | str | Callable, optional): Logger instance, identifier, or callable returning a logger.

    Returns:
        Callable: The wrapped function.
    """

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger_instance = get_logger_from_decorator_param(param_logger, args)
            if logger_instance is None:
                raise ValueError("[time_tracker] A logger must be specified via param_logger.")

            start_time = time.perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                elapsed_time = time.perf_counter() - start_time
                log_message = f"{get_function_metadata(func, args, kwargs)} executed in {elapsed_time:.6f}s"
                logger_instance.debug(log_message)

        return wrapper

    return decorator


def log(param_logger: Logger | str | Callable = None, log_level: LogLevels = LogLevels.DEBUG):
    """
    Decorator to log function/method calls at a specified log level.

    Args:
        param_logger (Logger | str | Callable, optional): Logger instance, identifier, or callable returning a logger.
        log_level (LogLevels, optional): Logging level. Defaults to LogLevels.DEBUG.

    Returns:
        Callable: The wrapped function.
    """

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger_instance = get_logger_from_decorator_param(param_logger, args)
            if logger_instance is None:
                raise ValueError("[log] A logger must be specified via param_logger.")

            logger_instance.log(f"{get_function_metadata(func, args, kwargs)} called", log_level)
            return func(*args, **kwargs)

        return wrapper

    return decorator
