from logger import Logger, LogLevels

from brain.synchronous_wrappers import SynchronousWrapper
from brain.dict_proxy import DictProxyAccessor

from typing import TypeVar, Type, List, Callable, Coroutine
from multiprocessing import Process

import functools
import inspect
import asyncio

TBrain = TypeVar("TBrain", bound="Brain")


class Brain:
    """
    The brain is a main controller of applications.
    It manages tasks which can be routines or one-shot tasks.
    It is also able to manage subprocesses.
    How to use it ?
    - Create a child class of Brain
    - In the child's __init__ first define all attributes, who will use through the brain.
    Then, at the END of the __init__ method, call super().__init__(logger, self).
    Every child's __init__ parameters will be instantiated as attributes available in the brain.
    - Transform your method into task by using the decorator @Brain.task()
    - Classic task (executed in the main process), they have to be asynchronous
        * Create a one-shot task by using the decorator @Brain.task() (it will be executed only once and in the
        main process)
        * Create a routine task by using the decorator @Brain.task(refresh_rate=<refresh rate you want>) (it will be
        executed periodically according to the refresh rate and in the main process)
    - Subprocess task (executed in a subprocess), they have to be synchronous
        * Create a subprocess one-shot task by using the decorator @Brain.task(process=True) (it will be executed only
        once in a subprocess)
        * Create a routine subprocess task by using the decorator @Brain.task(
        refresh_rate=<refresh rate you want>, process=True) (it will be executed periodically according to the refresh
        and in a subprocess)
    - Get the tasks by calling the method brain.get_tasks() and add them to the background tasks of the application

    -> Be careful by using subprocesses, the shared data between the main process and the subprocesses is limited,
    only serializable data can be shared. More over the data synchronization is not real-time, it is done by a routine.
    Subprocesses are useful to execute heavy tasks or tasks that can block the main process.
    """

    def __init__(self, logger: Logger, child: TBrain) -> None:
        """
        This constructor have to be called in the end of  __init__ method of the child class.
        By using super().__init__(logger, self)
        """
        if logger is None:
            raise ValueError("Logger is required for the brain to work properly.")
        self.logger = logger

        self.__shared_self = DictProxyAccessor()
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

        # Add attributes name to shared_self, it will be used by logger to identify the source of the logs
        self.__shared_self.name = self.__str__()

    """
        Task decorator
    """

    @classmethod
    def task(cls, refresh_rate: float or int = -1, process=False, define_loop_later=False,
             start_loop_marker="# ---Loop--- #"):
        """
        Decorator to add a task function to the brain. There are 3 cases:
        - If the task has a refresh rate, it becomes a 'routine' (perpetual task)
        - If the task has no refresh rate, it becomes a 'one-shot' task
        - If the task is a subprocess, it becomes a 'subprocess' task --> it can also be a 'routine'
        or a 'one-shot' task (depending on the refresh rate)
        """

        def decorator(func: Callable[[TBrain], None]):
            if not hasattr(cls, "tasks"):
                cls.tasks = []

            cls.tasks.append((func, refresh_rate, process, define_loop_later, start_loop_marker))
            return func

        return decorator

    """
        Async functions wrappers
    """

    async def __async_safe_execute(self, func, error_sleep: float or int = 0.5):
        try:
            await func(self)
        except Exception as error:
            self.logger.log(
                f"Brain [{self}]-[{func.__name__}] error: {error}",
                LogLevels.ERROR,
            )
            await asyncio.sleep(max(error_sleep, 0.5))  # Avoid spamming the logs

    async def __async_wrap_to_routine(self, task, refresh_rate):
        self.logger.log(
            f"Brain [{self}], routine [{task.__name__}] started", LogLevels.INFO
        )
        while True:
            await self.__async_safe_execute(task, error_sleep=refresh_rate)
            await asyncio.sleep(refresh_rate)

    async def __async_wrap_to_one_shot(self, task):
        self.logger.log(
            f"Brain [{self}], task [{task.__name__}] started", LogLevels.INFO
        )
        await self.__async_safe_execute(task)
        self.logger.log(
            f"Brain [{self}], task [{task.__name__}] ended", LogLevels.INFO
        )

    """
        Task evaluation 
    """

    def __evaluate_task(self, task, refresh_rate, is_process, define_loop_later, start_loop_marker):
        """
            Evaluate the type of the task and add it to the list of async functions or processes.
        """
        # Process task (only synchronous tasks), create a process then add it in the process list
        if is_process:
            # One-shot task
            if define_loop_later:
                if refresh_rate is None or refresh_rate < 0:
                    raise ValueError(
                        f"Error while evaluate [{task.__name__}] task: it a process with a "
                        f"'define_loop_later' but no refresh rate is defined.")
                process_task = functools.partial(
                    SynchronousWrapper.sync_wrap_routine_with_initialization,
                    self.__shared_self, task, refresh_rate, start_loop_marker
                )
            elif refresh_rate == -1:
                process_task = functools.partial(
                    SynchronousWrapper.sync_wrap_to_one_shot,
                    self.__shared_self, task
                )
            # Routine task
            else:
                process_task = functools.partial(
                    SynchronousWrapper.sync_wrap_to_routine,
                    self.__shared_self, task, refresh_rate
                )
            self.__processes.append(Process(target=process_task))

        # Classic task executed in the main process (only asynchronous tasks), add it to the list of async functions
        else:
            # One-shot task
            if refresh_rate == -1:
                async_task = self.__async_wrap_to_one_shot(task)
            # Routine task
            else:
                async_task = self.__async_wrap_to_routine(task, refresh_rate)
            self.__async_functions.append(lambda: async_task)

    """
        Background routines enabling the subprocesses to operate
    """

    async def __start_subprocesses(self, _):
        """
        It is a one-shot task dedicating to start all processes.
        * Need to be wrap by one-shot task wrapper.
        * Add this method in the async functions list only if a subprocess task is defined.
        """
        for process in self.__processes:
            process.start()

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
        for task, refresh_rate, subprocess, define_loop_later, start_loop_marker in self.tasks:
            self.__evaluate_task(task, refresh_rate, subprocess, define_loop_later, start_loop_marker)

        # Add a one-shot task to start all processes if there are any
        if any(is_process for _, _, is_process, _, _ in self.tasks):
            self.__async_functions.append(
                lambda: self.__async_wrap_to_one_shot(self.__start_subprocesses)
            )
            self.__async_functions.append(
                lambda: self.__async_wrap_to_routine(self.__sync_self_and_shared_self, 0)
            )

        return self.__async_functions

    def __str__(self) -> str:
        return self.__class__.__name__
