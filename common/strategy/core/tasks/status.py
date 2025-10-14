"""Enumerations describing the execution status of a task."""

from __future__ import annotations

from enum import Enum, auto


class TaskStatus(Enum):
    """Enumeration of task execution statuses.

    Attributes:
        PENDING: Task is pending execution.
        IN_PROGRESS: Task is currently in progress.
        DONE: Task has been completed.
        FAILED: Task has failed.
        TIMEOUT: Task has timed out.
    """

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
