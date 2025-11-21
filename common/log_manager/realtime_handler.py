"""Real-time database logging handler for loggerplusplus.

This module provides a logging handler that can be attached to any loggerplusplus
Logger instance to automatically write logs to a SQLite database in real-time,
without modifying the loggerplusplus library.
"""

from __future__ import annotations

import datetime
import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING, override

from log_manager.database import LogDatabase
from log_manager.utils import detect_execution_boundary, parse_log_line

if TYPE_CHECKING:
    from logging import LogRecord


class RealtimeDBHandler(logging.Handler):
    """Logging handler that writes to SQLite database in real-time.

    This handler can be attached to any Python logger (including loggerplusplus
    loggers) to automatically write all log messages to a SQLite database as
    they are generated.

    The database structure is compatible with the log_manager indexer, so you
    can use all the existing query and analysis tools.
    """

    CATEGORY_PATTERN: re.Pattern[str] = re.compile(r"\[([A-Z_]+(?::[A-Za-z0-9:]+)?)\]")
    """Category pattern: [CATEGORY] or [CATEGORY:SubCategory]"""

    def __init__(
        self,
        db_path: Path | str,
        log_file_path: Path | str,
    ) -> None:
        """Initialize the realtime database handler.

        Args:
            db_path (Path | str): Path to SQLite database file
            log_file_path (Path | str): Path to the log file being written
        """
        super().__init__()
        self.db_path = Path(db_path)
        self.log_file_path = Path(log_file_path)
        self.db: LogDatabase | None = None
        self.current_execution_id: str | None = None
        self.current_date: str | None = None

        self._initialize_database()
        self._initialize_execution()

    def _initialize_database(self) -> None:
        """Create database connection and tables if they don't exist."""
        self.db = LogDatabase(self.db_path)
        self.current_date = self.log_file_path.stem

    def _initialize_execution(self) -> None:
        """Initialize a new execution for this logging session."""
        if not self.db:
            return

        existing_executions = self.db.get_executions(str(self.log_file_path))

        exec_num = 0
        if existing_executions:
            last_exec_id = existing_executions[-1]["execution_id"]
            exec_num = int(last_exec_id.split("_exec")[-1])

        self.current_execution_id = f"{self.current_date}_exec{exec_num:03d}"

        start_time = datetime.datetime.now()
        self.db.add_execution(
            execution_id=self.current_execution_id,
            start_time=start_time,
            log_file=str(self.log_file_path),
            description=f"Execution {exec_num}",
        )

    @staticmethod
    def _should_exclude_record(record: LogRecord) -> bool:
        """Check if a log record should be excluded from database.

        Args:
            record (LogRecord): The log record to check

        Returns:
            bool: True if the record should be excluded
        """
        pathname = record.pathname.replace("\\", "/")
        return any(pattern in pathname for pattern in [".venv", "site-packages"])

    @override
    def emit(self, record: LogRecord) -> None:
        """Emit a log record to the database.

        Args:
            record (LogRecord): The log record to emit
        """
        if not self.db or not self.current_execution_id:
            return

        if self._should_exclude_record(record):
            return

        try:
            message = record.getMessage()

            if detect_execution_boundary(message):
                existing_executions = self.db.get_executions(str(self.log_file_path))
                exec_num = len(existing_executions)
                self.current_execution_id = f"{self.current_date}_exec{exec_num:03d}"

                start_time = datetime.datetime.fromtimestamp(record.created)
                self.db.add_execution(
                    execution_id=self.current_execution_id,
                    start_time=start_time,
                    log_file=str(self.log_file_path),
                    description=f"Execution {exec_num}",
                )

            raw_line = self.format(record)
            parsed = parse_log_line(raw_line, current_date=self.current_date)
            if not parsed:
                return
            self.db.add_log_entry(
                execution_id=self.current_execution_id,
                **parsed,
            )

        except Exception:  # noqa: BLE001
            self.handleError(record)

    @override
    def close(self) -> None:
        """Close the database handler and update execution end time."""
        if self.db and self.current_execution_id:
            self.db.update_execution_end_time(
                self.current_execution_id,
                datetime.datetime.now(),
            )

            self.db.close()
            self.db = None

        super().close()
