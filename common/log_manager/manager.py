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
            logs_dir (Path | str): Directory containing log files. Defaults to 'logs'.
        """
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(exist_ok=True)

    def _get_db_path(self, log_file: str) -> Path:
        """Get database path for a log file.

        Args:
            log_file (str): Log filename (e.g., '2025-11-06.log')

        Returns:
            Path: Path to database file
        """
        base_name = Path(log_file).stem
        return self.logs_dir / f"{base_name}.db"

    def index_log(self, log_file: str, *, force_reindex: bool) -> int:
        """Index a specific log file.

        Args:
            log_file (str): Log filename
            force_reindex (bool): Force re-indexing even if already indexed

        Returns:
            int: Number of entries indexed
        """
        log_path = self.logs_dir / log_file
        db_path = self._get_db_path(log_file)

        if force_reindex and db_path.exists():
            db_path.unlink()

        with LogDatabase(db_path) as db:
            indexer = LogIndexer(db)
            return indexer.index_log_file(log_path, force_reindex=force_reindex)

    def list_executions(self, log_file: str) -> list[dict[str, Any]]:
        """List all executions in a log file.

        Args:
            log_file (str): Log filename

        Returns:
            list[dict[str, Any]]: List of execution records
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
        level: str | list[str] | None = None,
        logger: str | None = None,
        category: str | None = None,
        file: str | None = None,
        line_number: int | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Filter logs with various criteria.

        Args:
            log_file (str): Log filename
            execution_id (str | None): Filter by execution ID. Defaults to None.
            level (str | list[str] | None): Filter by log level(s). Defaults to None.
            logger (str | None): Filter by logger name. Defaults to None.
            category (str | None): Filter by category. Defaults to None.
            file (str | None): Filter by source file. Defaults to None.
            line_number (int | None): Filter by source line number. Defaults to None.
            limit (int | None): Maximum results. Defaults to None.

        Returns:
            list[dict[str, Any]]: List of matching log entries
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
                line_number=line_number,
                limit=limit,
            )

    def export_logs(
        self,
        log_file: str,
        output_file: Path | str,
        **filters: Any,  # noqa: ANN401
    ) -> int:
        """Export filtered logs to a file.

        Args:
            log_file (str): Source log filename
            output_file (Path | str): Output file path
            **filters (Any): Filter criteria (same as filter_logs)

        Returns:
            int: Number of entries exported
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
        **filters: Any,  # noqa: ANN401
    ) -> None:
        """Display filtered logs to console.

        Args:
            log_file (str): Log filename
            colorize (bool): Whether to colorize output
            **filters (Any): Filter criteria (same as filter_logs)
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
