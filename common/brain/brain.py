from logger import Logger, LogLevels

from multiprocessing import Process, Manager
from multiprocessing.managers import DictProxy
import asyncio

from typing import TypeVar, Type, List, Callable, Coroutine
import inspect

TBrain = TypeVar("TBrain", bound="Brain")


class Brain:
    """
    The brain is a main controller of applications.
    """

    def __init__(self, logger: Logger, child: TBrain) -> None:
        """
        This constructor have to be called in the __init__ method of the child class.
        By using super().__init__(logger, self)
        """
        if logger is None:
            raise ValueError("Logger is required for the brain to work properly.")
        self.logger = logger

        self.__processes = []
        self.__async_functions = []  # Routine or one-shot tasks
        child.dynamic_init()

    def dynamic_init(self):
        """
        This method is used to dynamically initialize the instance with the parameters of the caller.
        * You only have to call this method in the __init__ method of the child class.
        By Using super().__init__(logger, self)
        * The attributes of the child class will be initialized, based on the parameters of the caller.
        They will have the same name as the parameters of the child's __init__.
        """
        # Get the frame of the caller (the __init__ method of the child class)
        frame = inspect.currentframe().f_back.f_back
        # Get the params of the frame
        params = frame.f_locals

        # Assign the params to the instance
        for name, value in params.items():
            if name not in ["self", "logger"]:
                setattr(self, name, value)


    @classmethod
    def task(cls, refresh_rate: float or int = -1, process=False):
        """
        Decorator to add a task function to the brain. There are 3 cases:
        - If the task has a refresh rate, it becomes a 'routine' (perpetual task)
        - If the task has no refresh rate, it becomes a 'one-shot' task
        - If the task is a subprocess, it becomes a 'subprocess' task --> it can also be a 'routine'
        or a 'one-shot' task (depending on the refresh rate)
        Parameters
        ----------
        refresh_rate
        process

        Returns
        -------

        """

        def decorator(func: Callable[[TBrain], None]):
            if not hasattr(cls, "tasks"):
                cls.tasks = []

            cls.tasks.append((func.__name__, refresh_rate, process))
            return func

        return decorator

    async def __safe_execute(self, func, error_sleep: float or int = 0.5):
        try:
            await func()
        except Exception as error:
            self.logger.log(
                f"Brain [{self}]-[{func.__name__}] error: {error}",
                LogLevels.ERROR,
            )
            await asyncio.sleep(error_sleep)

    async def __wrap_to_routine(self, task, refresh_rate):
        self.logger.log(
            f"Brain [{self}], routine [{task.__name__}] started", LogLevels.INFO
        )
        while True:
            await self.__safe_execute(task, error_sleep=refresh_rate)
            await asyncio.sleep(refresh_rate)

    async def __wrap_to_one_shot(self, task):
        self.logger.log(
            f"Brain [{self}], task [{task.__name__}] started", LogLevels.INFO
        )
        await self.__safe_execute(task)

    def __wrap_to_process(self, task):
        def __start_task(shared_self_proxy):
            print("__start_task")
            async def task_wrapper():
                print("task_wrapper")
                shared_self = AttrDictProxy(shared_self_proxy)
                await task(shared_self)

            # Exécute la coroutine dans une nouvelle boucle d'événements
            asyncio.run(task_wrapper())

        # Notez que vous passez self.__shared_self directement, sans le wrapper ici,
        # car __start_task s'occupe de l'envelopper dans AttrDictProxy.
        return Process(target=__start_task)

    def evaluate_task(self, task, refresh_rate, subprocess):
        # If the task is a subprocess add it to the list of subprocesses
        # If the task is a routine or a one-shot task, add it to a list of async functions

        # One shot task
        if refresh_rate == -1:
            task = self.__wrap_to_one_shot(task)

        # Routine
        else:
            task = self.__wrap_to_routine(task, refresh_rate)

        # Subprocess
        if subprocess:
            self.__processes.append(self.__wrap_to_process(task))
            self.__async_functions.append(
                lambda: self.start_subprocesses()

            )
        else:
            self.__async_functions.append(lambda: task)

    async def start_subprocesses(self):
        print("Z")
        for subprocess in self.__processes:
            print("a", subprocess)
            subprocess.start()

    def get_tasks(self):
        # Evaluate all tasks and add them to the list of async functions or processes
        for task, refresh_rate, subprocess in self.tasks:
            self.evaluate_task(getattr(self, task), refresh_rate, subprocess)

        # First add all async functions
        tasks = self.__async_functions

        # Then if there are processes, add a task to start them to tasks (it is a one-shot task)
        """        
        if self.__processes:
            x = self.__wrap_to_one_shot(
                    self.start_subprocesses()
                )
            tasks.append(
                lambda: self.start_subprocesses
            )
        """
        return tasks

    def __str__(self) -> str:
        return self.__class__.__name__



