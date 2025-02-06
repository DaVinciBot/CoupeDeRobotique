# ====== Standard Library Imports ======
from typing import Any

# ====== Internal Project Imports ======
from brain.execution_states import ExecutionStates


# ====== Class Part ======
class TaskOutput:
    """
    Represents the output of a task, including the result and its execution state.

    Attributes:
        result (Any): The result of the task execution.
        execution_state (ExecutionStates): The state of the task execution, indicating success, error, or timeout.
    """

    def __init__(self, result: Any, execution_state: ExecutionStates) -> None:
        """
        Initializes a TaskOutput instance.

        Args:
            result (Any): The result of the task execution.
            execution_state (ExecutionStates): The state of the task execution.
        """
        self.result: Any = result
        self.execution_state: ExecutionStates = execution_state

    def have_crashed(self) -> bool:
        """
        Determines whether the task has crashed.

        Returns:
            bool: True if the task execution resulted in an error, False otherwise.
        """
        return self.execution_state == ExecutionStates.ERROR_OCCURRED

    def have_timeout(self) -> bool:
        """
        Determines whether the task has timed out.

        Returns:
            bool: True if the task execution resulted in a timeout, False otherwise.
        """
        return self.execution_state == ExecutionStates.TIMEOUT

    def is_success(self) -> bool:
        """
        Determines whether the task was successful.

        Returns:
            bool: True if the task did not time out or crash, False otherwise.
        """
        return not self.have_timeout() and not self.have_crashed()

    def __str__(self) -> str:
        """
        Returns a string representation of the TaskOutput instance.

        Returns:
            str: A string describing the task output.
        """
        return f"TaskOutput: result={self.result}, execution_state={self.execution_state.name}"

    def __repr__(self) -> str:
        """
        Returns the official string representation of the TaskOutput instance.

        Returns:
            str: A string describing the task output.
        """
        return self.__str__()
