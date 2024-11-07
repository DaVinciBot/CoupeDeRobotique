from logger import LogLevels
from utils import Utils

from brain.dict_proxy import DictProxyAccessor
from brain.execution_states import ExecutionStates
from multiprocessing import Process

import functools
import inspect
import time
import asyncio

from typing import TypeVar

TBrain = TypeVar("TBrain", bound="Brain")

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
    def safe_execute(self: DictProxyAccessor, func, error_sleep: float or int = 0.5):
        """
        It executes the function and logs the error if there is one
        :param self: the shared_self which has to be synchronized with the main process
        :param func: the function to execute
        :param error_sleep: the time to sleep in case of error
        :return:
        """
        try:
            return func(self)
        except Exception as error:
            self.logger.log(
                f"[{func.__name__}] executor (Subprocess: sync function) -> error: {error}",
                LogLevels.ERROR,
            )
            time.sleep(error_sleep)
            return ExecutionStates.ERROR_OCCURRED

    @staticmethod
    def wrap_to_routine(self, task, refresh_rate):
        """
        It wraps the function into a routine which is executed every refresh_rate seconds
        * It logs the start of the routine
        :param self: the shared_self which has to be synchronized with the main process
        :param task: the function to execute
        :param refresh_rate: the time to sleep between each execution
        :return:
        """
        self.logger.log(
            f"[{task.__name__}] routine (Subprocess: sync function) -> started",
            LogLevels.INFO,
        )
        while True:
            SynchronousWrapper.safe_execute(self, task, error_sleep=refresh_rate)
            time.sleep(refresh_rate)

    @staticmethod
    def wrap_to_one_shot(self, task):
        """
        It wraps the function into a one-shot task which is executed once
        * It logs the start of the task
        :param self: the shared_self which has to be synchronized with the main process
        :param task: the function to execute
        :return:
        """
        self.logger.log(
            f"[{task.__name__}] one-shot (Subprocess: sync function) -> started",
            LogLevels.INFO,
        )
        output = SynchronousWrapper.safe_execute(self, task)
        self.logger.log(
            f"[{task.__name__}] one-shot (Subprocess: sync function) -> ended, "
            f"output [{output}]",
            LogLevels.INFO,
        )
        return output

    @staticmethod
    async def wrap_timeout_task(self, task, timeout, task_name=None):
        if task_name is None:
            task_name = task.__name__

        self.logger.log(
            f"[{task_name}] timed task (Subprocess: sync function) -> started",
            LogLevels.INFO,
        )
        try:
            process = Process(target=task)
            process.start()

            run_start = Utils.get_ts()

            def run_duration():
                return Utils.time_since(run_start)

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
                return ExecutionStates.CORRECTLY

            else:
                self.logger.log(
                    f"[{task_name}] timed task (Subprocess: sync function) -> "
                    f"ended by reaching the timeout [{timeout}]",
                    LogLevels.INFO,
                )
                return ExecutionStates.TIMEOUT
        except Exception as error:
            self.logger.log(
                f"[{task_name}] timed task (Subprocess: sync function) -> "
                f"ended because an error occurred [{error}]",
                LogLevels.INFO,
            )
            return ExecutionStates.ERROR_OCCURRED

    """
        Specific to synchronous task (task executed as subprocess)
    """

    @staticmethod
    async def wrap_to_dummy_async(task):
        process = Process(target=task)
        process.start()
        # process.join()

    @staticmethod
    def wrap_routine_with_initialization(self, task, refresh_rate, start_loop_marker):
        """
        Wraps a task function into a routine with initialization and repetitive execution phases.

        Parameters:
        - self: Instance to be synchronized with the main process.
        - task: Function to execute, containing initialization and loop parts divided by start_loop_marker.
        - refresh_rate: Time to sleep between each execution in seconds.
        - start_loop_marker: Unique string to separate the initialization part from the loop part within the task function.
        """
        src = inspect.getsource(task)
        original_signature = get_task_name(task)

        # Removing the function signature while preserving indentation
        src = remove_task_signature(src)

        # Checking for the presence of the loop marker in the source code
        if start_loop_marker not in src:
            raise ValueError(
                f"The start loop marker '{start_loop_marker}' was not found in the source code."
            )

        # Splitting the source code into initialization and loop parts using the loop marker
        parts = src.split(start_loop_marker)
        if len(parts) < 2:
            raise ValueError(
                "The source code does not contain distinct parts separated by the marker."
            )

        # Extact the two function parts: initialization and loop
        init_src, loop_src = parts[0], start_loop_marker.join(parts[1:])

        # Prepapre the init function
        # Add a return statement to the initialization part to return all local variables which has been initialized
        init_src = init_src + "return locals()"
        # Create a new function with the initialization part
        init_code = f"def {original_signature}__init_func(self):\n    " + "\n    ".join(
            init_src.split("\n")
        )

        # Compiling and executing the initialization part
        local_vars = {}
        exec(init_code, task.__globals__, local_vars)
        init_func = local_vars[f"{original_signature}__init_func"]
        var_initialized = SynchronousWrapper.wrap_to_one_shot(self, init_func)

        # Prepare the loop function
        # Get all parameters of the loop function
        param_list = ", ".join(var_initialized.keys())
        # Create a new function with the loop part
        loop_code = (
            f"def {original_signature}__loop_func({param_list}):\n    "
            + "\n    ".join(loop_src.split("\n"))
        )

        # Compiling and executing the initialization part
        exec(loop_code, task.__globals__, local_vars)
        loop_func = local_vars[f"{original_signature}__loop_func"]
        # Create a partial function with the initialized variables except the self instance because it is given in sync_wrap_to_routine
        loop_func_partial_initialized = functools.partial(
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
    async def safe_execute(self: TBrain, func, error_sleep: float or int = 0.5):
        try:
            return await func(self)
        except Exception as error:
            self.logger.log(
                f"[{func.__name__}] executor (Main-process: async function) -> error: {error}",
                LogLevels.ERROR,
            )
            await asyncio.sleep(max(error_sleep, 0.5))  # Avoid spamming the logs
            return ExecutionStates.ERROR_OCCURRED

    @staticmethod
    async def wrap_to_routine(self: TBrain, task, refresh_rate: float or int):
        self.logger.log(
            f"[{task.__name__}] routine (Main-process: async function) -> started",
            LogLevels.INFO,
        )
        while True:
            await AsynchronousWrapper.safe_execute(self, task, error_sleep=refresh_rate)
            await asyncio.sleep(refresh_rate)

    @staticmethod
    async def wrap_to_one_shot(self, task):
        self.logger.log(
            f"[{task.__name__}] one-shot (Main-process: async function) -> started",
            LogLevels.INFO,
        )
        output = await AsynchronousWrapper.safe_execute(self, task)
        self.logger.log(
            f"[{task.__name__}] one-shot (Main-process: async function) -> ended, "
            f"output [{output}]",
            LogLevels.INFO,
        )
        return output

    @staticmethod
    async def wrap_timeout_task(self, task, timeout, task_name=None):
        if task_name is None:
            task_name = task.__name__

        self.logger.log(
            f"[{task_name}] timed task (Main-process: async function) -> started",
            LogLevels.INFO,
        )
        try:

            async def coroutine_executor():
                await task

            run_start = Utils.get_ts()
            await asyncio.wait_for(coroutine_executor(), timeout=timeout)

            self.logger.log(
                f"[{task_name}] timed task (Main-process: async function) -> "
                f"ended before the timeout [{(Utils.time_since(run_start)):.1f}s/{timeout:.1f}s]",
                LogLevels.INFO,
            )
            return ExecutionStates.CORRECTLY
        except asyncio.TimeoutError:
            self.logger.log(
                f"[{task_name}] timed task (Main-process: async function) -> "
                f"ended by reaching the timeout [{timeout}]",
                LogLevels.INFO,
            )
            return ExecutionStates.TIMEOUT
        except Exception as error:
            self.logger.log(
                f"[{task_name}] timed task (Main-process: async function) -> "
                f"ended because an error occurred [{error}]",
                LogLevels.INFO,
            )
            return ExecutionStates.ERROR_OCCURRED


"""
    Tools
"""


def get_task_name(task):
    """
    Returns the name of the task function.
    """
    return task.__name__


def remove_task_signature(src):
    """
    Removes the signature of the task function from the source code.
    * Without delete the indentation.
    """
    signature_end_index = src.find(":") + 1
    newline_after_signature_index = src.find("\n", signature_end_index)
    if newline_after_signature_index == -1:
        raise ValueError("Unable to find the function body.")

    return "\n" + src[newline_after_signature_index + 1 :]
