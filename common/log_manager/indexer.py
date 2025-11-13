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
    ) -> dict[str, Any] | None:
        """Parse a single log line.

        Args:
            line: Log line to parse

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

    @staticmethod
    def _should_skip_entry(
        parsed: dict[str, Any],
        last_entry: dict[str, Any] | None,
    ) -> tuple[bool, bool]:
        """Determine if a log entry should be skipped during incremental indexing.

        Args:
            parsed: Currently parsed log entry
            last_entry: Last indexed log entry from database

        Returns:
            tuple[bool, bool]: Tuple of (should_skip, should_exit_skip_mode):
                - should_skip: True if this entry should be skipped
                - should_exit_skip_mode: True if we should exit skip mode after this
        """
        if not last_entry:
            return (False, True)

        current_ts = parsed["timestamp"]
        last_ts = last_entry["timestamp"]

        if current_ts < last_ts:
            return (True, False)

        if current_ts == last_ts:
            current_location = f"{parsed['file_name']}:{parsed['line_number']}"
            last_location = f"{last_entry['file_name']}:{last_entry['line_number']}"

            if current_location == last_location:
                return (True, True)

            return (False, False)

        return (False, True)

    def index_log_file(
        self,
        log_file: Path | str,
        *,
        force_reindex: bool = False,  # TODO: argument cli
    ) -> int:
        """Index a log file into the database.

        Args:
            log_file: Path to log file
            force_reindex: If True, re-index even if already indexed

        Returns:
            int: Number of log entries indexed

        Raises:
            FileNotFoundError: If the log file does not exist
        """
        log_path = Path(log_file)
        if not log_path.exists():
            msg = f"Log file not found: {log_path}"
            raise FileNotFoundError(msg)

        self.current_date = log_path.stem

        last_entry = (
            None
            if force_reindex
            else self.db.get_last_log_entry(
                str(log_path),
            )
        )

        existing_executions = self.db.get_executions(str(log_path))
        existing_exec_ids = {e["execution_id"] for e in existing_executions}

        execution_counter = 0
        if existing_executions:
            last_exec_id = existing_executions[-1]["execution_id"]
            execution_counter = int(last_exec_id.split("_exec")[-1])
            self.current_execution_id = last_exec_id

        entries_indexed = 0
        skipping_mode = last_entry is not None

        with log_path.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                parsed = self._parse_log_line(line)
                if not parsed:
                    continue

                if skipping_mode:
                    should_skip, should_exit_skip_mode = self._should_skip_entry(
                        parsed,
                        last_entry,
                    )
                    if should_exit_skip_mode:
                        skipping_mode = False
                    if should_skip:
                        continue

                if self._detect_execution_boundary(line):
                    new_execution_counter = execution_counter + 1
                    new_execution_id = (
                        f"{self.current_date}_exec{new_execution_counter:03d}"
                    )

                    if new_execution_id not in existing_exec_ids:
                        execution_counter = new_execution_counter
                        self.current_execution_id = new_execution_id

                        start_time = datetime.fromisoformat(parsed["timestamp"])
                        self.db.add_execution(
                            execution_id=self.current_execution_id,
                            start_time=start_time,
                            log_file=str(log_path),
                            description=f"Execution {execution_counter}",
                        )
                        existing_exec_ids.add(self.current_execution_id)
                    else:
                        execution_counter = new_execution_counter
                        self.current_execution_id = new_execution_id

                if not self.current_execution_id:
                    self.current_execution_id = f"{self.current_date}_exec000"
                    if self.current_execution_id not in existing_exec_ids:
                        self.db.add_execution(
                            execution_id=self.current_execution_id,
                            start_time=datetime.fromisoformat(
                                f"{self.current_date} 00:00:00",
                            ),
                            log_file=str(log_path),
                            description="Execution 0",
                        )
                        existing_exec_ids.add(self.current_execution_id)

                if not self.db.log_entry_exists(
                    parsed["timestamp"],
                    parsed["file_name"],
                    parsed["line_number"],
                ):
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
