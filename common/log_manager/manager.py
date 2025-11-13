"""Main log manager interface."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from log_manager.database import LogDatabase
from log_manager.indexer import LogIndexer


class LogManager:
    """High-level interface for log management."""

    def __init__(self, logs_dir: Path | str = "logs") -> None:
        """Initialize log manager.

        Args:
            logs_dir: Directory containing log files
        """
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(exist_ok=True)

    def _get_db_path(self, log_file: str) -> Path:
        """Get database path for a log file.

        Args:
            log_file: Log filename (e.g., '2025-11-06.log')

        Returns:
            Path to database file
        """
        base_name = Path(log_file).stem
        return self.logs_dir / f"{base_name}.db"

    def index_log(self, log_file: str) -> int:
        """Index a specific log file.

        Args:
            log_file: Log filename

        Returns:
            Number of entries indexed
        """
        log_path = self.logs_dir / log_file
        db_path = self._get_db_path(log_file)

        with LogDatabase(db_path) as db:
            indexer = LogIndexer(db)
            return indexer.index_log_file(log_path)

    def list_executions(self, log_file: str) -> list[dict[str, Any]]:
        """List all executions in a log file.

        Args:
            log_file: Log filename

        Returns:
            List of execution records
        """
        db_path = self._get_db_path(log_file)

        if not db_path.exists():
            return []

        with LogDatabase(db_path) as db:
            return db.get_executions()

    def filter_logs(
        self,
        log_file: str,
        execution_id: str | None = None,
        level: str | None = None,
        logger: str | None = None,
        category: str | None = None,
        file: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Filter logs with various criteria.

        Args:
            log_file: Log filename
            execution_id: Filter by execution ID
            level: Filter by log level
            logger: Filter by logger name
            category: Filter by category
            file: Filter by source file
            limit: Maximum results

        Returns:
            List of matching log entries
        """
        db_path = self._get_db_path(log_file)

        if not db_path.exists():
            return []

        if execution_id == "last":
            executions = self.list_executions(log_file)
            execution_id = executions[-1]["execution_id"] if executions else None
        elif execution_id and len(execution_id) <= 3:
            while len(execution_id) < 3:
                execution_id = "0" + execution_id

        with LogDatabase(db_path) as db:
            return db.query_logs(
                execution_id=execution_id,
                level=level,
                logger_name=logger,
                category=category,
                file_name=file,
                limit=limit,
            )

    def export_logs(
        self,
        log_file: str,
        output_file: Path | str,
        **filters: Any,
    ) -> int:
        """Export filtered logs to a file.

        Args:
            log_file: Source log filename
            output_file: Output file path
            **filters: Filter criteria (same as filter_logs)

        Returns:
            Number of entries exported
        """
        logs = self.filter_logs(log_file, **filters)

        output_path = Path(output_file)
        with output_path.open("w", encoding="utf-8") as f:
            for entry in logs:
                f.write(entry["raw_line"] + "\n")

        return len(logs)

    def show_logs(
        self,
        log_file: str,
        *,
        colorize: bool = True,
        **filters: Any,
    ) -> None:
        """Display filtered logs to console.

        Args:
            log_file: Log filename
            colorize: Whether to colorize output
            **filters: Filter criteria
        """
        logs = self.filter_logs(log_file, **filters)

        # Color codes
        colors = {
            "DEBUG": "\033[36m",  # Cyan
            "INFO": "\033[32m",  # Green
            "WARNING": "\033[33m",  # Yellow
            "ERROR": "\033[31m",  # Red
            "CRITICAL": "\033[35m",  # Magenta
            "RESET": "\033[0m",
        }

        for entry in logs:
            line = entry["raw_line"]

            if colorize:
                level = entry["level"]
                if level in colors:
                    line = line.replace(
                        f" {level} ",
                        f" {colors[level]}{level}{colors['RESET']} ",
                    )

            print(line)

        print(f"\n{len(logs)} entries found")
