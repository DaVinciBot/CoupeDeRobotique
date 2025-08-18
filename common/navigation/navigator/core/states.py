"""Navigator high-level states."""

from enum import Enum, auto


class NavigatorState(Enum):
    """Navigator state.

    Attributes:
        IDLE: No movement in progress.
        PLANNING: Path generation and trajectory planning.
        READY: Ready to move (trajectory ready but not started).
        MOVING: Execution of the movement in progress.
        PAUSED: Movement temporarily interrupted.
        FINISHED: Goal reached.
        STOPPED: Movement manually interrupted.
        REPLANNING: Recalculating path/trajectory.
        ERROR: Failure or blocking event (obstacle, timeout, etc.).

    """

    IDLE = auto()
    """No movement in progress."""
    PLANNING = auto()
    """Path generation and trajectory planning."""
    READY = auto()
    """Ready to move (trajectory ready but not started)."""
    MOVING = auto()
    """Execution of the movement in progress."""
    PAUSED = auto()
    """Movement temporarily interrupted."""
    FINISHED = auto()
    """Goal reached."""
    STOPPED = auto()
    """Movement manually interrupted."""
    REPLANNING = auto()
    """Recalculating path/trajectory."""
    ERROR = auto()
    """Failure or blocking event (obstacle, timeout, etc.)."""
