# ====== Code Summary ======
# This module provides logging and time-tracking decorators to enhance function/method monitoring.

# ====== Imports ======
# Standard library imports
from typing import Callable
from functools import wraps
import time

# Internal project imports
from logger.logger import Logger
from logger.log_levels import LogLevels
from logger.tools import get_function_metadata, get_logger_from_decorator_param
# ====== Tools functions ======


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
