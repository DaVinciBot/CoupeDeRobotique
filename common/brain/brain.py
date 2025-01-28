# ====== Standard Library Imports ======
import inspect
import asyncio
from types import FrameType
from typing import TypeVar, Any, Callable

# ====== Internal Project Imports ======
from logger import Logger, LogLevels

from brain.task import Task, AsynchronousWrapper
from brain.dict_proxy import DictProxyAccessor

# ====== Type Hints ======
TBrain = TypeVar("TBrain", bound="Brain")


# ====== Class Part ======
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

        Args:
            logger (Logger): Logger instance for logging.
            child (TBrain): The child class instance.
        """
        if logger is None:
            raise ValueError("Logger is required for the brain to work properly.")
        self.logger: Logger = logger

        self.__shared_self: DictProxyAccessor = DictProxyAccessor(name=child.__str__())
        self.__processes: list = []
        self.__async_functions: list = []

        child.dynamic_init()

    """
        Dynamic initialization
    """

    def dynamic_init(self) -> None:
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
        frame: FrameType = inspect.currentframe().f_back.f_back
        # Get the params of the frame
        params: dict[str, Any] = frame.f_locals

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
                if DictProxyAccessor.is_serialized(value):
                    setattr(self.shared_self, name, value)
                else:
                    self.logger.log(
                        f"[dynamic_init] cannot serialize attribute [{name}].",
                        LogLevels.WARNING,
                    )

    """
        Properties
    """

    @property
    def shared_self(self) -> DictProxyAccessor:
        """
        Accessor for the shared state (for subprocess interactions).

        Returns:
            DictProxyAccessor: The shared state.
        """
        return self.__shared_self

    """
        Task decorator
    """

    @classmethod
    def task(
            cls: type[TBrain],
            # Force to define parameter by using param=... synthax
            *,
            # Force user to define there params
            process: bool,
            run_on_start: bool,
            # Params with default value
            refresh_rate: float | int = -1,
            timeout: int = -1,
            define_loop_later: bool = False,
            start_loop_marker="# ---Loop--- #",
    ) -> Callable:
        """
        Decorator to add a task function to the brain. There are 3 cases:
        - If the task has a refresh rate, it becomes a 'routine' (perpetual task)
        - If the task has no refresh rate, it becomes a 'one-shot' task
        - If the task is a subprocess, it becomes a 'subprocess' task --> it can also be a 'routine'
        or a 'one-shot' task (depending on the refresh rate)

        Args:
            process (bool): If True, the task runs in a subprocess.
            run_on_start (bool): If True, the task runs at the application's start.
            refresh_rate (float | int, optional): Frequency of execution for routine tasks. Defaults to -1.
            timeout (int, optional): Timeout for the task. Defaults to -1.
            define_loop_later (bool, optional): If True, allows defining the task loop later. Defaults to False.
            start_loop_marker (str, optional): Marker for the start of the loop. Defaults to "# ---Loop--- #".

        Returns:
            Callable: Decorated function as a task.
        """

        def decorator(func: Callable) -> Callable:
            if not hasattr(cls, "_tasks"):
                cls._tasks: list[Task] = []

            cls._tasks.append(
                Task(
                    func,
                    process,
                    run_on_start,
                    refresh_rate,
                    timeout,
                    define_loop_later,
                    start_loop_marker,
                )
            )
            return func

        return decorator

    """
        Task evaluation
    """

    def __evaluate_task(self, task: Task) -> None:
        """
        Evaluates a task and categorizes it into processes or async functions based on its configuration.

        Args:
            task (Task): The task to evaluate.

        Returns:
            None
        """
        if task.run_to_start:
            evaluated_task = task.evaluate(
                brain_executor=self, shared_brain_executor=self.shared_self
            )
            if task.is_process:
                self.__processes.append(evaluated_task)
            else:
                self.__async_functions.append(lambda: evaluated_task)
        else:

            async def coroutine_executor():
                return await task.evaluate(
                    brain_executor=self, shared_brain_executor=self.shared_self
                )

            setattr(self, task.name, coroutine_executor)

    """
        Background routines enabling the subprocesses to operate
    """

    async def __start_subprocesses(self, _) -> None:
        """
        Routine to start all subprocess tasks.

        Returns:
            None
        """
        await asyncio.gather(*self.__processes)

    async def __sync_self_and_shared_self(self, _) -> None:
        """
        It is a routine task dedicating to synchronize the attributes of the instance with the shared_self.
        Need to be a routine with a very low refresh rate.
        * Need to be wrap by routine task wrapper.
        * Add this method in the async functions list only if a subprocess task is defined.

        Returns:
            None
        """
        for key in self.shared_self.get_dict().keys():
            self_attr_value = getattr(self, key)
            self_shared_attr_value = eval(f"self.shared_self.{key}")

            # Verify if the value is different between the instance and the shared data
            if self_attr_value != self_shared_attr_value:
                # The value has changed on the virtual self ?
                if key in self.shared_self.get_updated_attributes():
                    setattr(self, key, self_shared_attr_value)
                    self.shared_self.remove_updated_attribute(key)
                else:
                    setattr(self.shared_self, key, self_attr_value)

    """
        Get evaluated tasks which need to be added to the background tasks of the application
    """

    def get_tasks(self) -> list:
        """
        Evaluates all tasks and prepares them for execution, adding subprocess routines as needed.

        Returns:
            list: A list of async functions ready for execution.
        """
        # Evaluate all tasks and add them to the list of async functions or processes
        if hasattr(self, "_tasks"):
            for task in self._tasks:
                self.__evaluate_task(task)

            # Add a one-shot task to start all processes and routine to synchronize self_shared and self
            if any(task.is_process for task in self._tasks):
                self.__async_functions.append(
                    lambda: AsynchronousWrapper.wrap_to_one_shot(
                        self, self.__start_subprocesses
                    )
                )
                self.__async_functions.append(
                    lambda: AsynchronousWrapper.wrap_to_routine(
                        self, self.__sync_self_and_shared_self, 0.01
                    )
                )

        return self.__async_functions

    def __str__(self) -> str:
        """
        Returns the name of the class as its string representation.

        Returns:
            str: The class name.
        """
        return self.__class__.__name__
