# ====== Standard Library Imports ======
from enum import IntEnum


# ====== Class Part ======
class ExecutionStates(IntEnum):
    """
    Enumeration representing the possible states of task execution.

    Attributes:
        CORRECTLY (int): Indicates successful execution of the task.
        TIMEOUT (int): Indicates the task execution timed out.
        ERROR_OCCURRED (int): Indicates an error occurred during task execution.
    """
    CORRECTLY: int = 0
    TIMEOUT: int = 1
    ERROR_OCCURRED: int = 2
