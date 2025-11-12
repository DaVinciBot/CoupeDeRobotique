"""SQLite database for log indexing."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from datetime import datetime


class LogDatabase:
    """Manages SQLite database for log indexing."""

    def __init__(self, db_path: Path | str) -> None:
        """Initialize database connection.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.conn: sqlite3.Connection | None = None
        self._initialize_database()

    def _initialize_database(self) -> None:
        """Create database and tables if they don't exist."""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row

        cursor = self.conn.cursor()

        # Create executions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                execution_id TEXT UNIQUE NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                log_file TEXT NOT NULL,
                description TEXT
            )
        """)

        # Create logs table with full indexing
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                execution_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                level TEXT NOT NULL,
                logger_name TEXT NOT NULL,
                file_name TEXT,
                line_number INTEGER,
                category TEXT,
                message TEXT NOT NULL,
                raw_line TEXT NOT NULL,
                line_offset INTEGER NOT NULL,
                FOREIGN KEY (execution_id) REFERENCES executions(execution_id)
            )
        """)

        # Create indexes for fast searching
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_execution ON logs(execution_id)",
        )
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_level ON logs(level)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_logger ON logs(logger_name)",
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_category ON logs(category)",
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_file ON logs(file_name)",
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_timestamp ON logs(timestamp)",
        )

        self.conn.commit()

    def add_execution(
        self,
        execution_id: str,
        start_time: datetime,
        log_file: str,
        description: str | None = None,
    ) -> None:
        """Register a new execution.

        Args:
            execution_id: Unique identifier for this execution
            start_time: When the execution started
            log_file: Path to the log file
            description: Optional description
        """
        if not self.conn:
            return

        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR IGNORE INTO executions
            (execution_id, start_time, log_file, description)
            VALUES (?, ?, ?, ?)
        """,
            (
                execution_id,
                start_time.isoformat(),
                log_file,
                description,
            ),
        )
        self.conn.commit()

    def update_execution_end_time(
        self,
        execution_id: str,
        end_time: datetime,
    ) -> None:
        """Update the end time of an execution.

        Args:
            execution_id: Execution identifier
            end_time: When the execution ended
        """
        if not self.conn:
            return

        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE executions SET end_time = ? WHERE execution_id = ?
        """,
            (end_time.isoformat(), execution_id),
        )
        self.conn.commit()

    def add_log_entry(
        self,
        execution_id: str,
        timestamp: str,
        level: str,
        logger_name: str,
        message: str,
        raw_line: str,
        line_offset: int,
        file_name: str | None = None,
        line_number: int | None = None,
        category: str | None = None,
    ) -> None:
        """Add a log entry to the database.

        Args:
            execution_id: Execution this log belongs to
            timestamp: Log timestamp
            level: Log level (INFO, WARNING, etc.)
            logger_name: Name of the logger
            message: Log message
            raw_line: Original log line
            line_offset: Byte offset in log file
            file_name: Source file name
            line_number: Source line number
            category: Category prefix (e.g., NAV:Task)
        """
        if not self.conn:
            return

        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO logs
            (execution_id, timestamp, level, logger_name, file_name,
             line_number, category, message, raw_line, line_offset)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                execution_id,
                timestamp,
                level,
                logger_name,
                file_name,
                line_number,
                category,
                message,
                raw_line,
                line_offset,
            ),
        )
        self.conn.commit()

    def get_executions(self, log_file: str | None = None) -> list[dict[str, Any]]:
        """Get all executions, optionally filtered by log file.

        Args:
            log_file: Optional log file filter

        Returns:
            List of execution dictionaries
        """
        if not self.conn:
            return []

        cursor = self.conn.cursor()

        if log_file:
            cursor.execute(
                """
                SELECT * FROM executions
                WHERE log_file = ?
                ORDER BY start_time DESC
            """,
                (log_file,),
            )
        else:
            cursor.execute("SELECT * FROM executions ORDER BY start_time DESC")

        return [dict(row) for row in cursor.fetchall()]

    def query_logs(
        self,
        execution_id: str | None = None,
        level: str | None = None,
        logger_name: str | None = None,
        category: str | None = None,
        file_name: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Query logs with filters.

        Args:
            execution_id: Filter by execution
            level: Filter by log level
            logger_name: Filter by logger name
            category: Filter by category prefix
            file_name: Filter by source file
            limit: Maximum number of results

        Returns:
            List of log entry dictionaries
        """
        if not self.conn:
            return []

        cursor = self.conn.cursor()

        query = "SELECT * FROM logs WHERE 1=1"
        params: list[Any] = []

        if execution_id:
            query += " AND execution_id = ?"
            params.append(execution_id)

        if level:
            query += " AND level = ?"
            params.append(level)

        if logger_name:
            query += " AND logger_name LIKE ?"
            params.append(f"%{logger_name}%")

        if category:
            query += " AND category LIKE ?"
            params.append(f"%{category}%")

        if file_name:
            query += " AND file_name LIKE ?"
            params.append(f"%{file_name}%")

        query += " ORDER BY timestamp ASC"

        if limit:
            query += f" LIMIT {limit}"

        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def close(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self) -> LogDatabase:
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.close()
