from logger import Logger, LogLevels
from utils import Utils

from brain.task_wrappers import SynchronousWrapper, AsynchronousWrapper
from brain.dict_proxy import DictProxyAccessor
from brain.task import Task

from typing import TypeVar, Type, List, Callable, Coroutine
from multiprocessing import Process
import threading

import functools
import inspect
import asyncio

TBrain = TypeVar("TBrain", bound="Brain")


class Brain:

    def __init__(self, logger: Logger, child: TBrain) -> None:
        """
        This constructor have to be called in the end of  __init__ method of the child class.
        By using super().__init__(logger, self)
        """
        if logger is None:
            raise ValueError("Logger is required for the brain to work properly.")
        self.logger = logger

        self.__shared_self = DictProxyAccessor(name=child.__str__())
        self.__processes = []
        self.__async_functions = []

        child.dynamic_init()

    """
        Dynamic initialization
    """

    def dynamic_init(self):
        """
        This method is used to dynamically initialize the instance with the parameters of the caller.
        * You only have to call this method in the __init__ method of the child class.
        By Using super().__init__(logger, self)
        * The attributes of the child class will be initialized, based on the parameters of the caller.
        They will have the same name as the parameters of the child's __init__.
        * This method will also instantiate the shared_self attribute, which is a clone of the actual self but
        accessible by processes. It is a DictProxyAccessor object. It will only contain public and serializable attributes.
        """
        # Get the frame of the caller (the __init__ method of the child class)
        frame = inspect.currentframe().f_back.f_back
        # Get the params of the frame
        params = frame.f_locals

        # Assign the params if child __init__ to the instance as attributes
        for name, value in params.items():
            if name not in ["self", "logger"]:
                setattr(self, name, value)

        # Add the attributes to the shared_self (for subprocesses), when possible (serializable)
        for name, value in vars(self).items():
            # Get only public attributes
            if (
                    not name.startswith("__")
                    and not name.startswith("_")
                    and name != "self"
            ):
                # Try to serialize the attribute
                try:
                    setattr(self.__shared_self, name, value)
                except Exception as error:
                    self.logger.log(
                        f"Brain [{self}]-[dynamic_init] cannot serialize attribute [{name}]. ({error})",
                        LogLevels.WARNING
                    )

    """
        Properties
    """

    @property
    def shared_self(self):
        return self.__shared_self

    """
        Task decorator
    """

    @classmethod
    def task(cls,
             # Force to define parameter by using param=... synthax
             *,
             # Force user to define there params
             process: bool,
             run_on_start: bool,
             # Params with default value
             refresh_rate: float or int = -1,
             timeout: int = -1,
             define_loop_later: bool = False,
             start_loop_marker="# ---Loop--- #"
             ):
        """
        Decorator to add a task function to the brain. There are 3 cases:
        - If the task has a refresh rate, it becomes a 'routine' (perpetual task)
        - If the task has no refresh rate, it becomes a 'one-shot' task
        - If the task is a subprocess, it becomes a 'subprocess' task --> it can also be a 'routine'
        or a 'one-shot' task (depending on the refresh rate)
        """

        def decorator(func: Callable[[TBrain], None]):
            if not hasattr(cls, "_tasks"):
                cls._tasks = []

            cls._tasks.append(
                Task(func, process, run_on_start, refresh_rate, timeout, define_loop_later, start_loop_marker)
            )
            return func

        return decorator

    """
        Task evaluation
    """

    def __evaluate_task(self, task: Task):
        if task.run_to_start:
            evaluated_task = task.evaluate(brain_executor=self, shared_brain_executor=self.shared_self)
            if task.is_process:
                self.__processes.append(evaluated_task)
            else:
                self.__async_functions.append(lambda: evaluated_task)
        else:
            async def coroutine_executor():
                evaluated_task = task.evaluate(brain_executor=self, shared_brain_executor=self.shared_self)
                return await evaluated_task
            setattr(self, task.name, coroutine_executor)


    """
        Background routines enabling the subprocesses to operate
    """

    async def __start_subprocesses(self, _):
        await asyncio.gather(*self.__processes)

    async def __sync_self_and_shared_self(self, _):
        """
        It is a routine task dedicating to synchronize the attributes of the instance with the shared_self.
        Need to be a routine with a very low refresh rate.
        * Need to be wrap by routine task wrapper.
        * Add this method in the async functions list only if a subprocess task is defined.
        """
        self_shared_reference = self.__shared_self.get_dict()
        # Iterate on each attribute of the self instance (there are the only ones that can be synchronized)
        for key, value in self_shared_reference.items():
            # Verify if the value is different between the instance and the shared data
            if key != "name" and getattr(self, key) != getattr(self.__shared_self, key):
                # If different check the self_shared_reference value to know if it is the instance
                # or self_shared which have been updated
                if value != getattr(self.__shared_self, key):
                    # If the value is the instance one, update the shared data
                    setattr(self.__shared_self, key, getattr(self, key))
                    self_shared_reference[key] = getattr(self, key)  # Update also the reference
                else:
                    # If the value is the shared data one, update the instance
                    setattr(self, key, getattr(self.__shared_self, key))

    """
        Get evaluated tasks which need to be added to the background tasks of the application
    """

    def get_tasks(self):
        # Evaluate all tasks and add them to the list of async functions or processes
        if hasattr(self, "_tasks"):
            for task in self._tasks:
                self.__evaluate_task(task)

            # Add a one-shot task to start all processes and routine to synchronize self_shared and self
            if any(task.is_process for task in self._tasks):
                self.__async_functions.append(
                    lambda: AsynchronousWrapper.wrap_to_one_shot(self, self.__start_subprocesses)
                )
                self.__async_functions.append(
                    lambda: AsynchronousWrapper.wrap_to_routine(self, self.__sync_self_and_shared_self, 0)
                )

        return self.__async_functions

    def __str__(self) -> str:
        return self.__class__.__name__
