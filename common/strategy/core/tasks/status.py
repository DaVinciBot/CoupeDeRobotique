from enum import Enum, auto


class TaskStatus(Enum):
    PENDING = auto()
    IN_PROGRESS = auto()
    DONE = auto()
    FAILED = auto()
    TIMEOUT = auto()
