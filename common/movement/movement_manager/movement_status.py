from enum import Enum, auto


class MovementStatus(Enum):
    """
    Enum class for movement status.
    Represents various states related to movement outcomes.
    """
    SUCCESS = auto()  # Movement completed successfully
    CRASH = auto()  # Movement resulted in a crash
    NO_ACCESSIBLE = auto()  # Target area is not accessible
    INTERRUPT = auto()  # Movement was interrupted
    PENDING = auto()  # Movement is still in progress or pending
    NOT_STARTED = auto()  # Movement has not started
    TIMEOUT = auto()  # Movement took too long and timed out
    INVALID_COMMAND = auto()  # The command given was invalid
    BLOCKED = auto()  # Movement is blocked by an obstacle
    STALLED = auto()  # Movement stalled and could not proceed
    ACS = auto()  # Movement was stopped by the Anti-Collision System

    def is_finished(self) -> bool:
        """
        Check if the movement status indicates that the movement is not finished.
        """
        return self not in {MovementStatus.PENDING, MovementStatus.NOT_STARTED}
