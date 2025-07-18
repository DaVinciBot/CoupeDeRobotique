from enum import Enum, auto


class NavigatorTaskState(Enum):
    """Navigator task state.

    Attributes:
        NOT_PLANNED: The task is not planned.
        IN_PROGRESS: The task is in progress.
        AVOIDING: The task is avoiding an obstacle.
        ABORT: The task is aborted.
        STABILIZING: The task is stabilizing.
        FINISHED: The task is finished.
    """

    NOT_PLANNED = auto()  # The task is not planned.
    IN_PROGRESS = auto()  # The task is in progress.
    AVOIDING = auto()  # The task is avoiding an obstacle.
    ABORT = auto()  # The task is aborted.
    STABILIZING = auto()  # The task is stabilizing.
    FINISHED = auto()  # The task is finished.

    def is_finished(self) -> bool:
        """Check if the task is finished."""
        return self in {NavigatorTaskState.FINISHED, NavigatorTaskState.ABORT}
