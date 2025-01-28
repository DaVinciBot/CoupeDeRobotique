from typing import Callable, Optional
from functools import wraps
import time

from logger import LogLevels, Logger
from logger.constants import TRACK_TIME_STR


def time_tracker(get_logger: Optional[Callable] | Logger = None):
    """
    Decorator to track the execution time of a function and log it using the provided logger.

    Args:
        get_logger (Callable, optional): A function that takes an instance and returns a logger.
                                          Must be provided if decorating a method.

    Raises:
        ValueError: If get_logger is not provided.

    Returns:
        Callable: The decorated function with execution time tracking.
    """

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Obtain the logger dynamically
            logger = None
            if isinstance(get_logger, Logger):
                logger = get_logger
            elif get_logger is not None:
                instance = args[
                    0
                ]  # First argument of a bound method is the instance (self)
                logger = get_logger(instance)
            else:
                raise ValueError("A logger must be specified via get_logger.")

            # Measure the execution time
            start_time = time.perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                elapsed_time = time.perf_counter() - start_time
                logger.log(
                    f"Function `{func.__name__}` executed in {elapsed_time:.6f} seconds.",
                    level=LogLevels.DEBUG,
                )

        return wrapper

    return decorator
