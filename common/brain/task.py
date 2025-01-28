# ====== Standard Library Imports ======
import functools
from typing import TypeVar, Callable, Any, Optional, Coroutine

# ====== Internal Project Imports ======
from logger import LogLevels
from brain.task_wrappers import SynchronousWrapper, AsynchronousWrapper
from brain.task_output import TaskOutput

# ====== Type Hints ======
TBrain = TypeVar("TBrain", bound="Brain")
TDictProxyAccessor = TypeVar("TDictProxyAccessor", bound="DictProxyAccessor")


# ====== Class Part ======
class Task:
    """
    Represents a task with multiple execution modes such as one-shot, routine, or routine with initialization.
    The task can be evaluated in a process-based or classic asynchronous context.
    """

    def __init__(
            self,
            function: Callable[..., Any],
            is_process: bool,
            run_on_start: bool,
            refresh_rate: Optional[float],
            timeout: Optional[float],
            define_loop_later: bool,
            start_loop_marker: Optional[str],
    ) -> None:
        """
        Initializes a Task instance.

        Args:
            function (Callable): The function representing the task.
            is_process (bool): Whether the task runs in a separate process.
            run_on_start (bool): Whether the task should run on start.
            refresh_rate (Optional[float]): The time interval for repetitive execution.
            timeout (Optional[float]): The timeout for the task execution.
            define_loop_later (bool): Whether the task includes a loop defined later.
            start_loop_marker (Optional[str]): The marker to separate initialization and loop parts.
        """
        self._function: Callable[..., Any] = function
        self._is_process: bool = is_process
        self._run_on_start: bool = run_on_start
        self._refresh_rate: Optional[float] = refresh_rate
        self._timeout: Optional[float] = timeout
        self._define_loop_later: bool = define_loop_later
        self._start_loop_marker: Optional[str] = start_loop_marker

    @property
    def is_process(self) -> bool:
        """Indicates if the task runs as a separate process."""
        return self._is_process

    @property
    def name(self) -> str:
        """Returns the name of the task function."""
        return self._function.__name__

    @property
    def refresh_rate_is_set(self) -> bool:
        """Checks if the refresh rate is set and valid."""
        return self._refresh_rate is not None and self._refresh_rate >= 0

    @property
    def is_one_shot(self) -> bool:
        """Determines if the task is a one-shot execution."""
        return not self.refresh_rate_is_set and not self._define_loop_later

    @property
    def is_routine(self) -> bool:
        """Determines if the task is a routine execution."""
        return self.refresh_rate_is_set and not self._define_loop_later

    @property
    def is_routine_with_initialisation(self) -> bool:
        """Determines if the task is a routine with an initialization phase."""
        return self._define_loop_later

    @property
    def is_timed(self) -> bool:
        """Checks if the task has a timeout set."""
        return self._timeout is not None and self._timeout >= 0

    @property
    def run_to_start(self) -> bool:
        """Indicates if the task should run at the start."""
        return self._run_on_start

    def __evaluate_process_task(self, brain_executor: TDictProxyAccessor) -> Coroutine[Any, Any, TaskOutput]:
        """
        Evaluates a process-based task and returns the wrapped task.
        - Routine with initialisation (one-shoot then routine)
        - One-shot
        - Routine

        Args:
            brain_executor (TDictProxyAccessor): The shared brain executor for synchronization.

        Returns:
            Callable: The wrapped task.
        """
        # Routine with initialisation
        if self.is_routine_with_initialisation:
            # Check that the refresh rate has been set
            if not self.refresh_rate_is_set:
                raise ValueError(
                    f"Error while evaluate [{self.name}] task: it a process with a "
                    f"'define_loop_later' but no refresh rate is defined."
                )
            wrapped_task: Callable[..., Any] = functools.partial(
                SynchronousWrapper.wrap_routine_with_initialization,
                brain_executor,
                self._function,
                self._refresh_rate,
                self._start_loop_marker,
            )
        # One-shot
        elif self.is_one_shot:
            wrapped_task: functools.partial = functools.partial(
                SynchronousWrapper.wrap_to_one_shot, brain_executor, self._function
            )
        # Routine
        elif self.is_routine:
            wrapped_task: functools.partial = functools.partial(
                SynchronousWrapper.wrap_to_routine,
                brain_executor,
                self._function,
                self._refresh_rate,
            )
        # Unknown task type
        else:
            brain_executor.logger.log(
                f"Task-evaluation: error while wrapping [{self.name}] task. Task type unknown !",
                LogLevels.ERROR,
            )
            raise ValueError(
                f"Task-evaluation: error while wrapping [{self.name}] task. Task type unknown !"
            )

        # Add a timeout -> we have to convert the synchronous function to async one !
        if self.is_timed:
            async_wrapped_task: Coroutine[Any, Any, TaskOutput] = SynchronousWrapper.wrap_timeout_task(
                brain_executor, wrapped_task, self._timeout, self.name
            )
        else:
            async_wrapped_task: Coroutine[Any, Any, TaskOutput] = SynchronousWrapper.wrap_to_dummy_async(wrapped_task)

        return async_wrapped_task

    def __evaluate_classic_task(self, brain_executor: TBrain) \
            -> Coroutine[Any, Any, TaskOutput] | Coroutine[Any, Any, None]:
        """
        Evaluates a classic asynchronous task and returns the wrapped task.
        - One-shot
        - Routine

        Args:
            brain_executor (TBrain): The main brain executor.

        Returns:
            Callable: The wrapped task.
        """
        # One-shot
        if self.is_one_shot:
            wrapped_task: Coroutine[Any, Any, TaskOutput] = AsynchronousWrapper.wrap_to_one_shot(
                brain_executor, self._function
            )
        # Routine
        elif self.is_routine:
            wrapped_task: Coroutine[Any, Any, None] = AsynchronousWrapper.wrap_to_routine(
                brain_executor, self._function, self._refresh_rate
            )
        # Unknown task type
        else:
            brain_executor.logger.log(
                f"Task-evaluation: error while wrapping [{self.name}] task. Task type unknown !",
                LogLevels.ERROR,
            )
            raise ValueError(
                f"Task-evaluation: error while wrapping [{self.name}] task. Task type unknown !"
            )

        # Add a timeout
        if self.is_timed:
            wrapped_task: Coroutine[Any, Any, TaskOutput] = AsynchronousWrapper.wrap_timeout_task(
                brain_executor, wrapped_task, self._timeout, self.name
            )

        return wrapped_task

    def evaluate(
            self, brain_executor: TBrain, shared_brain_executor: TDictProxyAccessor
    ) -> Coroutine[Any, Any, TaskOutput] | Coroutine[Any, Any, None]:
        """
        Evaluates the task based on its type (process-based or classic) and returns the wrapped task.

        Args:
            brain_executor (TBrain): The main brain executor.
            shared_brain_executor (TDictProxyAccessor): The shared brain executor for synchronization.

        Returns:
            Callable: The wrapped task.
        """
        if self.is_process:
            return self.__evaluate_process_task(shared_brain_executor)
        else:
            return self.__evaluate_classic_task(brain_executor)
