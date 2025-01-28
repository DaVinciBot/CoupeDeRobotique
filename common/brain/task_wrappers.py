# ====== Standard Library Imports ======
import time
from datetime import datetime

import asyncio
from multiprocessing import Process

import inspect
import functools

from typing import TypeVar, Callable, Any, Coroutine

# ====== Internal Project Imports ======
from logger import LogLevels
from brain.execution_states import ExecutionStates
from brain.dict_proxy import DictProxyAccessor
from brain.task_output import TaskOutput

# ====== Type Hints ======
TBrain = TypeVar("TBrain", bound="Brain")

# ====== Class Part ======
"""
    Synchronous Wrappers
"""


class SynchronousWrapper:
    """
    This static class is used to wrap synchronous functions into a routine or a one-shot task.
    * It add a safe execution of the function and logs what is going on.
    * These functions are used in the Brain class to wrap the subprocesses tasks.
    """

    """
        Common wrapper
    """

    @staticmethod
    def safe_execute(
            self: DictProxyAccessor, func: Callable[..., Any], error_sleep: float or int = 0.5
    ) -> TaskOutput:
        """
        It executes the function and logs the error if there is one
        Args:
            self (DictProxyAccessor): Shared instance synchronized with the main process.
            func (callable): Function to execute.
            error_sleep (float | int): Time to sleep in case of error.

        Returns:
            TaskOutput: Contains the result and execution state.
        """
        try:
            return TaskOutput(result=func(self), execution_state=ExecutionStates.CORRECTLY)
        except Exception as error:
            self.logger.log(
                f"[{func.__name__}] executor (Subprocess: sync function) -> error: {error}",
                LogLevels.ERROR,
            )
            time.sleep(error_sleep)
            return TaskOutput(result=None, execution_state=ExecutionStates.ERROR_OCCURRED)

    @staticmethod
    def wrap_to_routine(self: DictProxyAccessor, task: Callable[..., Any], refresh_rate: float | int) -> None:
        """
        It wraps the function into a routine which is executed every refresh_rate seconds
        * It logs the start of the routine
        Args:
            self (DictProxyAccessor): Shared instance synchronized with the main process.
            task (callable): Function to execute.
            refresh_rate (float): Time in seconds between executions.
        """
        self.logger.log(
            f"[{task.__name__}] routine (Subprocess: sync function) -> started",
            LogLevels.INFO,
        )
        while True:
            SynchronousWrapper.safe_execute(self, task, error_sleep=refresh_rate)
            time.sleep(refresh_rate)

    @staticmethod
    def wrap_to_one_shot(self: DictProxyAccessor, task: Callable[..., Any]) -> TaskOutput:
        """
        It wraps the function into a one-shot task which is executed once
        * It logs the start of the task

        Args:
            self (DictProxyAccessor): Shared instance synchronized with the main process.
            task (callable): Function to execute.

        Returns:
            TaskOutput: Contains the result and execution state.
        """
        self.logger.log(
            f"[{task.__name__}] one-shot (Subprocess: sync function) -> started",
            LogLevels.INFO,
        )
        output: TaskOutput = SynchronousWrapper.safe_execute(self, task)
        self.logger.log(
            f"[{task.__name__}] one-shot (Subprocess: sync function) -> ended, "
            f"output [{output}]",
            LogLevels.INFO,
        )
        return output

    @staticmethod
    async def wrap_timeout_task(
            self: DictProxyAccessor, task: Callable[[], None], timeout: float | int, task_name=None
    ) -> TaskOutput:
        """
        Executes a function with a timeout and logs its completion or timeout status.

        Args:
            self (DictProxyAccessor): Shared instance synchronized with the main process.
            task (callable): Function to execute.
            timeout (float): Maximum time allowed for the task.
            task_name (str, optional): Name of the task. Defaults to the function's name.

        Returns:
            TaskOutput: Contains the result and execution state.
        """
        if task_name is None:
            task_name: str = task.__name__

        self.logger.log(
            f"[{task_name}] timed task (Subprocess: sync function) -> started",
            LogLevels.INFO,
        )
        try:
            process: Process = Process(target=task)
            process.start()

            run_start: float = datetime.timestamp(datetime.now())

            def run_duration() -> float:
                """
                Returns the time elapsed since the task started.

                Returns:
                    float: Elapsed time in seconds.
                """
                return datetime.timestamp(datetime.now()) - run_start

            while process.is_alive() and run_duration() < timeout:
                await asyncio.sleep(0.1)

            process.terminate()
            process.join()

            if run_duration() < timeout:
                self.logger.log(
                    f"[{task_name}] timed task (Subprocess: sync function) -> "
                    f"ended before the timeout [{run_duration():.1f}s/{timeout:.1f}s]",
                    LogLevels.INFO,
                )
                # Can't get subprocess return value
                return TaskOutput(result=None, execution_state=ExecutionStates.CORRECTLY)

            else:
                self.logger.log(
                    f"[{task_name}] timed task (Subprocess: sync function) -> "
                    f"ended by reaching the timeout [{timeout}]",
                    LogLevels.INFO,
                )
                return TaskOutput(result=None, execution_state=ExecutionStates.TIMEOUT)
        except Exception as error:
            self.logger.log(
                f"[{task_name}] timed task (Subprocess: sync function) -> "
                f"ended because an error occurred [{error}]",
                LogLevels.INFO,
            )
            return TaskOutput(result=None, execution_state=ExecutionStates.ERROR_OCCURRED)

    """
        Specific to synchronous task (task executed as subprocess)
    """

    @staticmethod
    async def wrap_to_dummy_async(task: Callable[[], None]) -> TaskOutput:
        """
        Wraps a function into an asynchronous dummy task using a subprocess.

        Args:
            task (callable): Function to execute.

        Returns:
            TaskOutput: Contains the result and execution state.
        """
        process: Process = Process(target=task)
        process.start()
        return TaskOutput(result=None, execution_state=ExecutionStates.CORRECTLY)

    @staticmethod
    def wrap_routine_with_initialization(
            self: DictProxyAccessor, task: Callable[..., Any], refresh_rate: float | int, start_loop_marker: str
    ) -> None:
        """
        Wraps a task function into a routine with initialization and repetitive execution phases.

        Args:
            self (DictProxyAccessor): Shared instance synchronized with the main process.
            task (Callable): Function containing initialization and loop parts.
            refresh_rate (float | int): Time in seconds between loop executions.
            start_loop_marker (str): Unique marker to separate initialization and loop parts.
        """
        src: str = inspect.getsource(task)
        original_signature: str = get_task_name(task)

        # Removing the function signature while preserving indentation
        src: str = remove_task_signature(src)

        # Checking for the presence of the loop marker in the source code
        if start_loop_marker not in src:
            raise ValueError(
                f"The start loop marker '{start_loop_marker}' was not found in the source code."
            )

        # Splitting the source code into initialization and loop parts using the loop marker
        parts: list[str] = src.split(start_loop_marker)
        if len(parts) < 2:
            raise ValueError(
                "The source code does not contain distinct parts separated by the marker."
            )

        # Extact the two function parts: initialization and loop
        init_src: str = parts[0]
        loop_src: str = start_loop_marker.join(parts[1:])

        # Prepapre the init function
        # Add a return statement to the initialization part to return all local variables which has been initialized
        init_src: str = init_src + "return locals()"
        # Create a new function with the initialization part
        init_code: str = f"def {original_signature}__init_func(self):\n    " + "\n    ".join(
            init_src.split("\n")
        )

        # Compiling and executing the initialization part
        local_vars: dict[str, Any] = {}
        exec(init_code, task.__globals__, local_vars)
        init_func: Callable[..., dict[str, Any]] = local_vars[f"{original_signature}__init_func"]
        var_initialized: dict[str, Any] = SynchronousWrapper.wrap_to_one_shot(self, init_func).result

        # Prepare the loop function
        # Get all parameters of the loop function
        param_list: str = ", ".join(var_initialized.keys())
        # Create a new function with the loop part
        loop_code: str = (
                f"def {original_signature}__loop_func({param_list}):\n    "
                + "\n    ".join(loop_src.split("\n"))
        )

        # Compiling and executing the initialization part
        exec(loop_code, task.__globals__, local_vars)
        loop_func: Callable[..., None] = local_vars[f"{original_signature}__loop_func"]
        # Create a partial function with the initialized variables except the self instance because it is given in sync_wrap_to_routine
        loop_func_partial_initialized: functools.partial = functools.partial(
            loop_func, **{k: v for k, v in var_initialized.items() if k != "self"}
        )
        loop_func_partial_initialized.__name__ = f"{original_signature}__loop_func"
        SynchronousWrapper.wrap_to_routine(
            self, loop_func_partial_initialized, refresh_rate
        )


"""
    Asynchronous Wrappers
"""


class AsynchronousWrapper:
    @staticmethod
    async def safe_execute(
            self: TBrain, func: Callable[[TBrain], Any], error_sleep: float | int = 0.5
    ) -> TaskOutput:
        """
        Safely executes an asynchronous function and logs any errors that occur.

        Args:
            self (TBrain): Instance of the asynchronous environment.
            func (Callable): Async function to execute.
            error_sleep (float | int): Time to sleep in case of error.

        Returns:
            TaskOutput: Contains the result and execution state.
        """
        try:
            return TaskOutput(result=await func(self), execution_state=ExecutionStates.CORRECTLY)

        except Exception as error:
            self.logger.log(
                f"[{func.__name__}] executor (Main-process: async function) -> error: {error}",
                LogLevels.ERROR,
            )
            await asyncio.sleep(max(error_sleep, 0.5))  # Avoid spamming the logs
            return TaskOutput(result=None, execution_state=ExecutionStates.ERROR_OCCURRED)

    @staticmethod
    async def wrap_to_routine(self: TBrain, task: Callable[[TBrain], Any], refresh_rate: float | int) -> None:
        """
        Wraps an asynchronous function into a routine that executes repeatedly.

        Args:
          self (TBrain): Instance of the asynchronous environment.
          task (Callable): Async function to execute.
          refresh_rate (float | int): Time in seconds between executions.
        """
        self.logger.log(
            f"[{task.__name__}] routine (Main-process: async function) -> started",
            LogLevels.INFO,
        )
        while True:
            await AsynchronousWrapper.safe_execute(self, task, error_sleep=refresh_rate)
            await asyncio.sleep(refresh_rate)

    @staticmethod
    async def wrap_to_one_shot(self: TBrain, task: Callable[[TBrain], Any]) -> Coroutine[Any, Any, TaskOutput]:
        """
        Executes an asynchronous function as a one-shot task and logs its start and end.

        Args:
            self (TBrain): Instance of the asynchronous environment.
            task (Callable): Async function to execute.

        Returns:
            TaskOutput: Contains the result and execution state.
        """
        self.logger.log(
            f"[{task.__name__}] one-shot (Main-process: async function) -> started",
            LogLevels.INFO,
        )
        output: Coroutine[Any, Any, TaskOutput] = await AsynchronousWrapper.safe_execute(self, task)
        self.logger.log(
            f"[{task.__name__}] one-shot (Main-process: async function) -> ended, "
            f"output [{output}]",
            LogLevels.INFO,
        )
        return output

    @staticmethod
    async def wrap_timeout_task(
            self: TBrain, task: Coroutine[Any, Any, TaskOutput] | Coroutine[Any, Any, None], timeout: float | int,
            task_name: str | None = None
    ) -> TaskOutput:
        """
        Executes an asynchronous function with a timeout and logs its completion or timeout status.

        Args:
            self (TBrain): Instance of the asynchronous environment.
            task (Callable): Async function to execute.
            timeout (float | int): Maximum time allowed for the task.
            task_name (str, optional): Name of the task. Defaults to the function's name.

        Returns:
            TaskOutput: Contains the result and execution state.
        """
        if task_name is None:
            task_name: str = task.__name__

        self.logger.log(
            f"[{task_name}] timed task (Main-process: async function) -> started",
            LogLevels.INFO,
        )
        try:
            async def coroutine_executor() -> Any:
                # TODO: need to return await task() instead of just await task ?
                # return await task
                await task

            run_start: float = datetime.timestamp(datetime.now())
            output: Any = await asyncio.wait_for(coroutine_executor(), timeout=timeout)

            self.logger.log(
                f"[{task_name}] timed task (Main-process: async function) -> "
                f"ended before the timeout [{(datetime.timestamp(datetime.now()) - run_start):.1f}s/{timeout:.1f}s]",
                LogLevels.INFO,
            )
            return TaskOutput(result=output, execution_state=ExecutionStates.CORRECTLY)

        except asyncio.TimeoutError:
            self.logger.log(
                f"[{task_name}] timed task (Main-process: async function) -> "
                f"ended by reaching the timeout [{timeout}]",
                LogLevels.INFO,
            )
            return TaskOutput(result=None, execution_state=ExecutionStates.TIMEOUT)
        except Exception as error:
            self.logger.log(
                f"[{task_name}] timed task (Main-process: async function) -> "
                f"ended because an error occurred [{error}]",
                LogLevels.INFO,
            )
            return TaskOutput(result=None, execution_state=ExecutionStates.ERROR_OCCURRED)


"""
    Tools
"""


def get_task_name(task: Callable[..., Any]) -> str:
    """
    Returns the name of the task function.

    Args:
        task (Callable): Task function.

    Returns:
        str: Name of the task.
    """
    return task.__name__


def remove_task_signature(src: str) -> str:
    """
    Removes the signature of the task function from the source code.
    * Without delete the indentation.

    Args:
    src (str): Source code of the task function.

    Returns:
        str: Source code without the function signature.
    """
    signature_end_index: int = src.find(":") + 1
    newline_after_signature_index: int = src.find("\n", signature_end_index)
    if newline_after_signature_index == -1:
        raise ValueError("Unable to find the function body.")

    return "\n" + src[newline_after_signature_index + 1:]
