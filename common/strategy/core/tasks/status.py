from enum import Enum, auto


class TaskStatus(Enum):
    PENDING = auto()
    """Task is pending execution."""
    IN_PROGRESS = auto()
    """Task is currently in progress."""
    DONE = auto()
    """Task has been completed."""
    FAILED = auto()
    """Task has failed."""
    TIMEOUT = auto()
    """Task has timed out."""
