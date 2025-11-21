"""Log file parser and indexer."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from log_manager.utils import detect_execution_boundary, parse_log_line

if TYPE_CHECKING:
    from log_manager.database import LogDatabase


class LogIndexer:
    """Parses log files and indexes them in the database."""

    def __init__(self, db: LogDatabase) -> None:
        """Initialize indexer.

        Args:
            db (LogDatabase): Database instance to use for indexing
        """
        self.db = db
        self.current_execution_id: str | None = None
        self.current_date: str | None = None

    @staticmethod
    def _should_skip_entry(
        parsed: dict[str, Any],
        last_entry: dict[str, Any] | None,
    ) -> tuple[bool, bool]:
        """Determine if a log entry should be skipped during incremental indexing.

        Args:
            parsed (dict[str, Any]): Currently parsed log entry
            last_entry (dict[str, Any] | None): Last indexed log entry from database

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
        force_reindex: bool,
    ) -> int:
        """Index a log file into the database.

        Args:
            log_file (Path | str): Path to log file
            force_reindex (bool):
                If True, re-index even if already indexed.

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
                parsed = parse_log_line(line, current_date=self.current_date)
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

                if detect_execution_boundary(line):
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
