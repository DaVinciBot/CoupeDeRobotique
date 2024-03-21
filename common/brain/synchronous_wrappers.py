from logger import LogLevels

from brain.dict_proxy import DictProxyAccessor

import time


class SynchronousWrapper:
    """
    This static class is used to wrap synchronous functions into a routine or a one-shot task.
    * It add a safe execution of the function and logs what is going on.
    * These functions are used in the Brain class to wrap the subprocesses tasks.
    """

    @staticmethod
    def sync_safe_execute(self: DictProxyAccessor, func, error_sleep: float or int = 0.5) -> None:
        """
        It executes the function and logs the error if there is one
        :param self: the shared_self which has to be synchronized with the main process
        :param func: the function to execute
        :param error_sleep: the time to sleep in case of error
        :return:
        """
        try:
            func(self)
        except Exception as error:
            self.logger.log(
                f"Brain [{self.name}]-[{func.__name__}] error: {error}",
                LogLevels.ERROR,
            )
            time.sleep(error_sleep)

    @staticmethod
    def sync_wrap_to_routine(self, task, refresh_rate):
        """
        It wraps the function into a routine which is executed every refresh_rate seconds
        * It logs the start of the routine
        :param self: the shared_self which has to be synchronized with the main process
        :param task: the function to execute
        :param refresh_rate: the time to sleep between each execution
        :return:
        """
        self.logger.log(
            f"Brain [{self.name}], routine [{task.__name__}] started", LogLevels.INFO
        )
        while True:
            SynchronousWrapper.sync_safe_execute(self, task, error_sleep=refresh_rate)
            time.sleep(refresh_rate)

    @staticmethod
    def sync_wrap_to_one_shot(self, task):
        """
        It wraps the function into a one-shot task which is executed once
        * It logs the start of the task
        :param self: the shared_self which has to be synchronized with the main process
        :param task: the function to execute
        :return:
        """
        self.logger.log(
            f"Brain [{self.name}], task [{task.__name__}] started", LogLevels.INFO
        )
        SynchronousWrapper.sync_safe_execute(self, task)
