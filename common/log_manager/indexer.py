"""Log file parser and indexer."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from log_manager.database import LogDatabase


class LogIndexer:
    """Parses log files and indexes them in the database."""

    # Log format: HH:MM:SS.ffffff -> [logger] [file:line] LEVEL | message
    LOG_PATTERN = re.compile(
        r"(?P<time>\d{2}:\d{2}:\d{2}\.\d+)\s+->\s+"
        r"\[(?P<logger>[^\]]+)\]\s+"
        r"\[(?P<file>[^:]+):(?P<line>\d+)\]\s+"
        r"(?P<level>\w+)\s+\|\s+"
        r"(?P<message>.*)",
    )

    # Category pattern: [CATEGORY] or [CATEGORY:SubCategory]
    CATEGORY_PATTERN = re.compile(r"\[([A-Z]+(?::[A-Za-z0-9:]+)?)\]")

    def __init__(self, db: LogDatabase) -> None:
        """Initialize indexer.

        Args:
            db: Database instance to use for indexing
        """
        self.db = db
        self.current_execution_id: str | None = None
        self.current_date: str | None = None

    def _parse_log_line(
        self,
        line: str,
        offset: int,
    ) -> dict[str, Any] | None:
        """Parse a single log line.

        Args:
            line: Log line to parse
            offset: Byte offset in file

        Returns:
            Parsed log entry or None if parse failed
        """
        match = self.LOG_PATTERN.match(line)
        if not match:
            return None

        data = match.groupdict()

        category = None
        category_match = self.CATEGORY_PATTERN.search(data["message"])
        if category_match:
            category = category_match.group(1)

        if self.current_date:
            timestamp = f"{self.current_date} {data['time']}"
        else:
            timestamp = data["time"]

        return {
            "timestamp": timestamp,
            "level": data["level"],
            "logger_name": data["logger"].strip(),
            "file_name": data["file"].strip(),
            "line_number": int(data["line"]),
            "category": category,
            "message": data["message"],
            "raw_line": line.strip(),
            "line_offset": offset,
        }

    @staticmethod
    def _detect_execution_boundary(line: str) -> bool:
        """Detect if a log line indicates a new execution start.

        Args:
            line: Log line to check

        Returns:
            bool: True if this is an execution boundary
        """
        return "Initialized with host: 0.0.0.0, port: 8080" in line

    def index_log_file(
        self,
        log_file: Path | str,
        *,
        force_reindex: bool = False,
    ) -> int:
        """Index a log file into the database.

        Args:
            log_file: Path to log file
            force_reindex: If True, re-index even if already indexed

        Returns:
            Number of log entries indexed

        Raises:
            FileNotFoundError: If the log file does not exist
        """
        log_path = Path(log_file)
        if not log_path.exists():
            msg = f"Log file not found: {log_path}"
            raise FileNotFoundError(msg)

        # Extract date from filename (e.g., 2025-11-06.log)
        self.current_date = log_path.stem

        execution_counter = 0
        entries_indexed = 0
        current_offset = 0

        with log_path.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                # Track offset for later retrieval
                line_start = current_offset
                current_offset += len(line.encode("utf-8"))

                # Detect execution boundaries
                if self._detect_execution_boundary(line):
                    execution_counter += 1
                    self.current_execution_id = (
                        f"{self.current_date}_exec{execution_counter:03d}"
                    )

                    # Register execution in database
                    parsed = self._parse_log_line(line, line_start)
                    if parsed:
                        start_time = datetime.fromisoformat(parsed["timestamp"])
                        self.db.add_execution(
                            execution_id=self.current_execution_id,
                            start_time=start_time,
                            log_file=str(log_path),
                            description=f"Execution {execution_counter}",
                        )

                # Ensure we have an execution_id
                if not self.current_execution_id:
                    self.current_execution_id = f"{self.current_date}_exec000"
                    self.db.add_execution(
                        execution_id=self.current_execution_id,
                        start_time=datetime.fromisoformat(
                            f"{self.current_date} 00:00:00",
                        ),
                        log_file=str(log_path),
                        description="Execution 0",
                    )

                # Parse and index the log line
                parsed = self._parse_log_line(line, line_start)
                if parsed:
                    self.db.add_log_entry(
                        execution_id=self.current_execution_id,
                        **parsed,
                    )
                    entries_indexed += 1

        return entries_indexed

    def index_directory(
        self,
        log_dir: Path | str,
        pattern: str = "*.log",
    ) -> dict[str, int]:
        """Index all log files in a directory.

        Args:
            log_dir: Directory containing log files
            pattern: Glob pattern for log files

        Returns:
            Dictionary mapping filenames to number of entries indexed
        """
        log_path = Path(log_dir)
        results = {}

        for log_file in sorted(log_path.glob(pattern)):
            print(f"Indexing {log_file.name}...")
            try:
                count = self.index_log_file(log_file)
                results[log_file.name] = count
                print(f"  ✓ Indexed {count} entries")
            except Exception as e:
                print(f"  ✗ Error: {e}")
                results[log_file.name] = 0

        return results
