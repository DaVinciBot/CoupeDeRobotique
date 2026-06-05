"""Module pour mesurer le temps d'exécution des fonctions."""

import functools
import time
from typing import Any, Callable

DEBUG_MODE = False


def set_debug_mode(enabled: bool) -> None:
    """Active ou désactive le mode debug.

    Args:
        enabled (bool): True pour activer le mode debug, False sinon.
    """
    global DEBUG_MODE
    DEBUG_MODE = enabled


def timer(func: Callable) -> Callable:
    """Décorateur pour mesurer le temps d'exécution d'une fonction.

    Args:
        func (Callable): La fonction à chronométrer.

    Returns:
        Callable: La fonction wrapper avec chronométrage.
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if not DEBUG_MODE:
            return func(*args, **kwargs)

        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        elapsed_time = (end_time - start_time) * 1000  # Convertir en ms

        func_name = func.__name__
        class_name = ""
        if args and hasattr(args[0], "__class__"):
            class_name = f"{args[0].__class__.__name__}."

        print(f"⏱️  {class_name}{func_name}: {elapsed_time:.2f} ms")

        return result

    return wrapper
