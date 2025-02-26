# ====== Code Summary ======
# This module provides utility functions for logging and function metadata retrieval.
# - `center_and_limit`: Centers or truncates text with trailing dots.
# - `get_function_metadata`: Generates a metadata string for function calls.
# - `get_logger_from_decorator_param`: Resolves a logger instance from various input types.

# ====== Imports ======
# Standard library imports
from functools import lru_cache
from typing import Callable, Union, Any
import inspect

# Used to avoid circular imports and keep type hints
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logger.logger import Logger


@lru_cache(maxsize=100)
def center_and_limit(text: str, width: int, trailing_dots: int = 2):
    """
    Centers a given text within a specified width. If the text exceeds the width,
    it truncates the text and appends trailing dots.

    Args:
        text (str): The input text to be processed.
        width (int): The total width within which the text should be centered.
        trailing_dots (int, optional): The number of dots to append when truncating. Defaults to 2.

    Returns:
        str: The formatted text, either centered or truncated with dots.
    """
    return (
        (text[: width - trailing_dots] + "." * trailing_dots)  # Truncate and add dots if text is too long
        if len(text) > width
        else text.center(width)  # Otherwise, center the text
    )


def get_function_metadata(func: Callable, args, kwargs, max_params_length: int = 15) -> str:
    """
    Generate a concise string containing function/method metadata, including module, class (if applicable),
    function name, and parameter values. Optionally truncates long argument values.

    Args:
        func (Callable): The function being described.
        args (tuple): Positional arguments passed to the function.
        kwargs (dict): Keyword arguments passed to the function.
        max_params_length (int, optional): Maximum length for each argument's string representation. Defaults to 50.

    Returns:
        str: A formatted string containing function metadata.
    """
    frame = inspect.currentframe().f_back.f_back
    module_name = frame.f_globals["__name__"].split(".")[-1]  # Shortened module name
    class_name = args[0].__class__.__name__ if args and hasattr(args[0], "__class__") else None

    # Retrieve parameter names and values
    bound_args = inspect.signature(func).bind(*args, **kwargs)
    bound_args.apply_defaults()

    def truncate(value: Any) -> str:
        """Truncate string representation of a value if it exceeds max_length."""
        value_str = repr(value)
        return value_str if len(value_str) <= max_params_length else value_str[:max_params_length - 3] + '...'

    # Don't truncate if max_params_length is negative
    if max_params_length < 0:
        params_info = ", ".join(f"{k}={v}" for k, v in bound_args.arguments.items())
    else:
        params_info = ", ".join(f"{k}={truncate(v)}" for k, v in bound_args.arguments.items())

    return f"[{module_name}] {class_name + '.' if class_name else ''}{func.__name__}({params_info})"


def get_logger_from_decorator_param(param_logger: Union["Logger", str, Callable], args) -> Union["Logger", None]:
    """
    Retrieve a Logger instance from various possible inputs: an existing Logger, a string identifier, or
    a callable that returns a logger.

    Args:
        param_logger (Logger | str | Callable): The logger parameter passed to the decorator.
        args (tuple): Positional arguments passed to the decorated function.

    Returns:
        Logger | None: A Logger instance if successfully resolved, otherwise None.
    """
    from logger.logger import Logger

    if isinstance(param_logger, Logger):
        return param_logger
    if isinstance(param_logger, str):
        return Logger(identifier=param_logger, follow_logger_manager_rules=True)
    if param_logger is not None:
        instance = args[0]  # First argument of a bound method is typically `self`
        return param_logger(instance)
    return None


def unpack_dict(d: dict) -> dict:
    """
    Unpack all nested dictionaries into a single dictionary (non-recursive keys).
    If duplicate keys exist, values will be overwritten.
    """
    flat_dict = {}

    def recursive_unpack(sub_d):
        for k, v in sub_d.items():
            if isinstance(v, dict):
                recursive_unpack(v)
            else:
                flat_dict[k] = v

    recursive_unpack(d)
    return flat_dict
