from logger import Logger, LogLevels

from brain.task_wrappers import SynchronousWrapper, AsynchronousWrapper

import functools
from typing import TypeVar

TBrain = TypeVar("TBrain", bound="Brain")
TDictProxyAccessor = TypeVar("TDictProxyAccessor", bound="DictProxyAccessor")


class Task:
    def __init__(
        self,
        function,
        is_process,
        run_on_start,
        refresh_rate,
        timeout,
        define_loop_later,
        start_loop_marker,
    ):
        self._function = function
        self._is_process = is_process
        self._run_on_start = run_on_start
        self._refresh_rate = refresh_rate
        self._timeout = timeout
        self._define_loop_later = define_loop_later
        self._start_loop_marker = start_loop_marker

    @property
    def is_process(self) -> bool:
        return self._is_process

    @property
    def name(self) -> str:
        return self._function.__name__

    @property
    def refresh_rate_is_set(self) -> bool:
        return self._refresh_rate is not None and self._refresh_rate >= 0

    @property
    def is_one_shot(self) -> bool:
        return not self.refresh_rate_is_set and not self._define_loop_later

    @property
    def is_routine(self) -> bool:
        return self.refresh_rate_is_set and not self._define_loop_later

    @property
    def is_routine_with_initialisation(self) -> bool:
        return self._define_loop_later

    @property
    def is_timed(self) -> bool:
        return self._timeout is not None and self._timeout >= 0

    @property
    def run_to_start(self) -> bool:
        return self._run_on_start

    def __evaluate_process_task(self, brain_executor: TDictProxyAccessor):
        """
        - Routine with initialisation (one-shoot then routine)
        - One-shot
        - Routine
        """
        # Routine with initialisation
        if self.is_routine_with_initialisation:
            # Check that the refresh rate has been set
            if not self.refresh_rate_is_set:
                raise ValueError(
                    f"Error while evaluate [{self.name}] task: it a process with a "
                    f"'define_loop_later' but no refresh rate is defined."
                )
            wrapped_task = functools.partial(
                SynchronousWrapper.wrap_routine_with_initialization,
                brain_executor,
                self._function,
                self._refresh_rate,
                self._start_loop_marker,
            )
        # One-shot
        elif self.is_one_shot:
            wrapped_task = functools.partial(
                SynchronousWrapper.wrap_to_one_shot, brain_executor, self._function
            )
        # Routine
        elif self.is_routine:
            wrapped_task = functools.partial(
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
            async_wrapped_task = SynchronousWrapper.wrap_timeout_task(
                brain_executor, wrapped_task, self._timeout, self.name
            )
        else:
            async_wrapped_task = SynchronousWrapper.wrap_to_dummy_async(wrapped_task)

        return async_wrapped_task

    def __evaluate_classic_task(self, brain_executor: TBrain):
        """
        - One-shot
        - Routine
        """
        # One-shot
        if self.is_one_shot:
            wrapped_task = AsynchronousWrapper.wrap_to_one_shot(
                brain_executor, self._function
            )
        # Routine
        elif self.is_routine:
            wrapped_task = AsynchronousWrapper.wrap_to_routine(
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
            wrapped_task = AsynchronousWrapper.wrap_timeout_task(
                brain_executor, wrapped_task, self._timeout, self.name
            )

        return wrapped_task

    def evaluate(
        self, brain_executor: TBrain, shared_brain_executor: TDictProxyAccessor
    ):
        if self.is_process:
            return self.__evaluate_process_task(shared_brain_executor)
        else:
            return self.__evaluate_classic_task(brain_executor)
