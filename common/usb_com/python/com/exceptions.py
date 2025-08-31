"""USB communication exception types."""

from __future__ import annotations


class ComException(Exception):
    """Custom exception for communication-related errors.

    This exception is raised when a communication
    failure or protocol error occurs.
    """
