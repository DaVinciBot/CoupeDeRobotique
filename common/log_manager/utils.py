"""Utility functions for log management."""

import re
from typing import Any

LOG_PATTERN: re.Pattern[str] = re.compile(
    r"(?P<time>\d{2}:\d{2}:\d{2}\.\d+)\s+->\s+"
    r"\[(?P<logger>[^\]]+)\]\s+"
    r"\[(?P<file>[^:]+):(?P<line>\d+)\]\s+"
    r"(?P<level>\w+)\s+\|\s+"
    r"(?P<message>.*)",
)
"""Log format: HH:MM:SS.ffffff -> [logger] [file:line] LEVEL | message"""
CATEGORY_PATTERN: re.Pattern[str] = re.compile(r"\[([A-Z_]+(?::[A-Za-z0-9:]+)?)\]")
"""Category pattern: [CATEGORY] or [CAT_EG_ORY:SubCategory]"""


def parse_log_line(
    line: str,
    current_date: str | None = None,
) -> dict[str, Any] | None:
    """Parse a single log line.

    Args:
        line (str): Log line to parse.
        current_date (str | None): Current date for timestamp parsing. Defaults to None.

    Returns:
        dict[str, Any] | None: Parsed log entry or None if parse failed.
    """
    match = LOG_PATTERN.match(line)
    if not match:
        return None

    data = match.groupdict()

    category = None
    category_match = CATEGORY_PATTERN.search(data["message"])
    if category_match:
        category = category_match.group(1)

    timestamp = f"{current_date} {data['time']}" if current_date else data["time"]

    return {
        "timestamp": timestamp,
        "level": data["level"],
        "logger_name": data["logger"].strip(),
        "file_name": data["file"].strip(),
        "line_number": int(data["line"]),
        "category": category,
        "message": data["message"],
        "raw_line": line.strip(),
    }


def detect_execution_boundary(message: str) -> bool:
    """Detect if a log message indicates a new execution start.

    Args:
        message (str): Log message

    Returns:
        bool: True if this is an execution boundary
    """
    return "[INIT] Initializing all systems..." in message
