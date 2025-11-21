"""Real-time database logging handler for loggerplusplus.

This module provides a logging handler that can be attached to any loggerplusplus
Logger instance to automatically write logs to a SQLite database in real-time,
without modifying the loggerplusplus library.

Example:
    from loggerplusplus import Logger
    from log_manager.realtime_handler import RealtimeDBHandler

    logger = Logger(identifier="my_logger", path="logs")
    db_handler = RealtimeDBHandler.attach_to_logger(logger)

    logger.info("[INIT] Initializing all systems...")
    # Log is automatically written to database
"""

from __future__ import annotations

import datetime
import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING

from log_manager.database import LogDatabase

if TYPE_CHECKING:
    from logging import LogRecord

    from loggerplusplus import Logger


class RealtimeDBHandler(logging.Handler):
    """Logging handler that writes to SQLite database in real-time.

    This handler can be attached to any Python logger (including loggerplusplus
    loggers) to automatically write all log messages to a SQLite database as
    they are generated.

    The database structure is compatible with the log_manager indexer, so you
    can use all the existing query and analysis tools.
    """

    CATEGORY_PATTERN: re.Pattern[str] = re.compile(r"\[([A-Z]+(?::[A-Za-z0-9:]+)?)\]")
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

        if existing_executions:
            last_exec_id = existing_executions[-1]["execution_id"]
            exec_num = int(last_exec_id.split("_exec")[-1])
        else:
            exec_num = 0

        self.current_execution_id = f"{self.current_date}_exec{exec_num:03d}"

        start_time = datetime.datetime.now()
        self.db.add_execution(
            execution_id=self.current_execution_id,
            start_time=start_time,
            log_file=str(self.log_file_path),
            description=f"Execution {exec_num}",
        )

    def _extract_category(self, message: str) -> str | None:
        """Extract category from message.

        Args:
            message (str): Log message

        Returns:
            str | None: Extracted category or None
        """
        match = self.CATEGORY_PATTERN.search(message)
        return match.group(1) if match else None

    def _format_timestamp(self, record: LogRecord) -> str:
        """Format timestamp from LogRecord.

        Args:
            record (LogRecord): The log record

        Returns:
            str: Formatted timestamp
        """
        dt = datetime.datetime.fromtimestamp(record.created)
        return dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # milliseconds precision

    def _format_raw_line(self, record: LogRecord) -> str:
        """Format the raw log line as it appears in the file.

        Args:
            record (LogRecord): The log record

        Returns:
            str: Formatted raw log line
        """
        dt = datetime.datetime.fromtimestamp(record.created)
        time_str = dt.strftime("%H:%M:%S.%f")[:-3]  # HH:MM:SS.mmm

        return (
            f"{time_str} -> [{record.name}] "
            f"[{record.filename}:{record.lineno}] "
            f"{record.levelname} | {record.getMessage()}"
        )

    def _detect_execution_boundary(self, message: str) -> bool:
        """Detect if a log message indicates a new execution start.

        Args:
            message (str): Log message

        Returns:
            bool: True if this is an execution boundary
        """
        return "[INIT] Initializing all systems..." in message

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

            if self._detect_execution_boundary(message):
                if self.current_execution_id:
                    self.db.update_execution_end_time(
                        self.current_execution_id,
                        datetime.datetime.now(),
                    )

                existing_executions = self.db.get_executions(str(self.log_file_path))
                exec_num = len(existing_executions)
                self.current_execution_id = f"{self.current_date}_exec{exec_num:03d}"

                start_time = datetime.datetime.now()
                self.db.add_execution(
                    execution_id=self.current_execution_id,
                    start_time=start_time,
                    log_file=str(self.log_file_path),
                    description=f"Execution {exec_num}",
                )

            category = self._extract_category(message)
            timestamp = self._format_timestamp(record)
            raw_line = self._format_raw_line(record)

            self.db.add_log_entry(
                execution_id=self.current_execution_id,
                timestamp=timestamp,
                level=record.levelname,
                logger_name=record.name,
                file_name=record.filename,
                line_number=record.lineno,
                category=category,
                message=message,
                raw_line=raw_line,
            )

        except Exception:
            self.handleError(record)

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

    @classmethod
    def attach_to_logger(
        cls,
        logger: Logger,
        db_path: Path | str | None = None,
    ) -> RealtimeDBHandler:
        """Attach a realtime database handler to a loggerplusplus Logger.

        This is a convenience method that automatically configures the handler
        with the logger's settings.

        Args:
            logger: The loggerplusplus Logger instance
            db_path (Path | str | None): Optional custom database path.
                If None, uses {logger.config.path}/{date}.db

        Returns:
            RealtimeDBHandler: The attached handler instance

        Raises:
            ValueError:
                If the logger does not have a valid config with full_path attribute
        """
        # Get the log file path from the logger
        if not hasattr(logger, "config") or not hasattr(logger.config, "full_path"):
            msg = "Logger must have a config with full_path attribute"
            raise ValueError(msg)

        log_file_path = logger.config.full_path

        if db_path is None:
            log_dir = Path(logger.config.path)
            date_str = datetime.datetime.now().strftime("%Y-%m-%d")
            db_path = log_dir / f"{date_str}.db"

        handler = cls(db_path=db_path, log_file_path=log_file_path)
        handler.setLevel(logging.DEBUG)

        logger.logger.addHandler(handler)

        return handler
