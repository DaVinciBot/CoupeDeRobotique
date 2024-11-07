from enum import IntEnum


class ExecutionStates(IntEnum):
    CORRECTLY = 0
    TIMEOUT = 1
    ERROR_OCCURRED = 2
