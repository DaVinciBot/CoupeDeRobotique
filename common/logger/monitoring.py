# ====== Code Summary ======
# This module provides a `DiskMonitor` class for monitoring disk usage and log files within a specified directory.
# It includes functionalities for retrieving disk statistics, summarizing log files, and automatically cleaning logs
# when they exceed a defined threshold.

# ====== Imports ======
# Standard library imports
import os
import re
import shutil
import datetime
from enum import Enum
from typing import List
from dataclasses import dataclass

# Internal project imports
from logger.logger_configs import MonitorConfig


# ====== Enum for Storage Units ======
class Unit(Enum):
    """
    Enum representing different storage units.
    """
    Go = "Go"
    Mo = "Mo"
    Ko = "Ko"

    @property
    def factor(self) -> int:
        """
        Returns the corresponding factor for unit conversion.
        """
        return {"Go": 1024 ** 3, "Mo": 1024 ** 2, "Ko": 1024}.get(self.value, 1024 ** 3)

    @classmethod
    def from_string(cls, unit_str: str) -> "Unit":
        """
        Converts a string representation to a Unit enum value.
        Defaults to 'Go' if an unsupported unit is provided.
        """
        try:
            return cls(unit_str)
        except ValueError:
            print(f"Unit '{unit_str}' not supported. Defaulting to 'Go'.")
            return cls.Go


# ====== Data Classes for Disk and Log Information ======
@dataclass
class DiskUsage:
    """
    Represents disk usage statistics.
    """
    total: float
    used: float
    free: float
    usage_ratio: float


@dataclass
class LogFileInfo:
    """
    Represents details of an individual log file.
    """
    path: str
    size: float
    line_count: int


@dataclass
class LogFilesSummary:
    """
    Represents a summary of all log files in a directory.
    """
    files: List[LogFileInfo]
    total_size: float
    usage_ratio: float


# ====== Disk Monitor Class ======
class DiskMonitor:
    """
    Monitors disk usage and log files in a specified directory.
    Provides methods to check disk statistics, log file details, and clean logs if necessary.
    """

    def __init__(
            self, logger, directory: str, config: MonitorConfig
    ):
        """
        Initializes the DiskMonitor with monitoring parameters.

        Args:
            logger: Logger instance for logging information.
            directory (str): Directory to monitor.
            config (MonitorConfig): Configuration settings for monitoring.
        """
        self.logger = logger
        self.directory: str = directory
        self.unit: Unit = Unit.from_string(config.file_size_unit)
        self.size_precision: int = config.file_size_precision
        self.disk_threshold: float = config.disk_alert_threshold_percent
        self.log_threshold: float = config.log_files_size_alert_threshold_percent
        self.max_log_size: float = (
            config.max_log_file_size * self.unit.factor
            if config.max_log_file_size is not None
            else None
        )
        self.enable_monitoring_logs: bool = config.files_monitoring

    def convert_unit(self, size: float) -> float:
        """
        Converts a size value from bytes to the specified unit.
        """
        return round(size / self.unit.factor, self.size_precision)

    def get_disk_usage(self) -> DiskUsage:
        """
        Retrieves disk usage statistics for the monitored directory.
        """
        total, used, free = shutil.disk_usage(self.directory)
        return DiskUsage(
            total=self.convert_unit(total),
            used=self.convert_unit(used),
            free=self.convert_unit(free),
            usage_ratio=round(used / total, 2)
        )

    def get_log_files_info(self) -> LogFilesSummary:
        """
        Retrieves information about log files in the monitored directory.
        """
        if not os.path.isdir(self.directory):
            return LogFilesSummary(files=[], total_size=0, usage_ratio=0)

        log_files = []
        total_size = 0

        for root, _, files in os.walk(self.directory):
            for file in files:
                # Only consider log files
                if file.endswith(".log"):
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path)
                    with open(file_path, 'r') as f:
                        line_count = sum(1 for _ in f)
                    log_files.append(
                        LogFileInfo(
                            path=file_path,
                            size=self.convert_unit(file_size),
                            line_count=line_count
                        )
                    )
                    total_size += file_size

        return LogFilesSummary(
            files=log_files,
            total_size=self.convert_unit(total_size),
            usage_ratio=round(total_size / shutil.disk_usage(self.directory)[0], 2)
        )

    @staticmethod
    def extract_date(filename: str) -> datetime.datetime | None:
        match = re.search(r"\d{8}", filename)
        if match:
            try:
                return datetime.datetime.strptime(match.group(), "%Y-%m-%d")
            except ValueError:
                return None
        return None

    def clean_logs(self) -> None:
        if self.enable_monitoring_logs:
            self.logger.info("=== Logs Cleaning Info ===")

        if self.max_log_size is None:
            self.logger.info("Log cleanup is disabled.")
            return

        log_summary = self.get_log_files_info()
        total_size_bytes = log_summary.total_size * self.unit.factor

        if total_size_bytes <= self.max_log_size:
            self.logger.info(
                f"Log size within limits "
                f"({log_summary.total_size}{self.unit.value}"
                f"/"
                f"{self.convert_unit(self.max_log_size)}{self.unit.value})."
            )
            return

        logs_with_dates = []
        for log in log_summary.files:
            log_date = self.extract_date(os.path.basename(log.path))
            if log_date:
                logs_with_dates.append((log_date, log))
            else:
                self.logger.warning(f"Log file {log.path} has an invalid date format. Deleting it.")
                try:
                    os.remove(log.path)
                    total_size_bytes -= log.size * self.unit.factor
                    self.logger.info(f"Deleted log with invalid date format: {log.path} ({log.size} {self.unit.value})")
                except Exception as e:
                    self.logger.error(f"Failed to delete {log.path}: {str(e)}")

        sorted_logs = [log for _, log in sorted(logs_with_dates, key=lambda x: x[0])]
        self.logger.info("Starting log cleanup...")

        while total_size_bytes > self.max_log_size and sorted_logs:
            oldest_file = sorted_logs.pop(0)
            try:
                os.remove(oldest_file.path)
                total_size_bytes -= oldest_file.size * self.unit.factor
                self.logger.info(f"Deleted log: {oldest_file.path} ({oldest_file.size} {self.unit.value})")
            except Exception as e:
                self.logger.error(f"Failed to delete {oldest_file.path}: {str(e)}")

        self.logger.info("Log cleanup completed.")

    def display_disk_usage(self) -> None:
        """
        Logs the current disk usage statistics.
        """
        disk_usage = self.get_disk_usage()
        self.logger.info("=== Disk Monitoring ===")
        self.logger.info(f"Total disk space: {disk_usage.total} {self.unit.value}")
        self.logger.info(f"Used space: {disk_usage.used} {self.unit.value} ({disk_usage.usage_ratio * 100:.2f}%)")
        self.logger.info(f"Free space: {disk_usage.free} {self.unit.value}")

        if disk_usage.usage_ratio >= self.disk_threshold:
            self.logger.warning(f"Disk usage exceeded {self.disk_threshold * 100:.0f}%!")

    def display_log_files(self) -> None:
        """
        Logs information about log files.
        """
        log_summary = self.get_log_files_info()
        self.logger.info("=== Log Files Info ===")
        self.logger.info(f"Number of logs: {len(log_summary.files)}")
        for log_file in log_summary.files:
            self.logger.info(f"{log_file.path} ({log_file.size} {self.unit.value}, {log_file.line_count} lines)")
        self.logger.info(f"Total log lines: {sum([f.line_count for f in log_summary.files])}")
        self.logger.info(f"Total log size: {log_summary.total_size} {self.unit.value}")
        self.logger.info(f"Log storage usage: {log_summary.usage_ratio * 100:.2f}%")

    def display_monitoring(self) -> None:
        """
        Logs disk and log file information.
        """
        self.display_disk_usage()
        self.display_log_files()
