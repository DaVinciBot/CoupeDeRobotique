from enum import Enum, auto


class NavigatorTaskState(Enum):
    NOT_PLANNED = auto()
    IN_PROGRESS = auto()
    AVOIDING = auto()
    ABORT = auto()
    FINISHED = auto()

    def is_finished(self) -> bool:
        return self in {
            NavigatorTaskState.FINISHED,
            NavigatorTaskState.ABORT
        }

