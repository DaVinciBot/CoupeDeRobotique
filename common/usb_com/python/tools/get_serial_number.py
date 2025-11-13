"""Utilities to list serial numbers of connected devices."""

from __future__ import annotations

import serial.tools.list_ports
from loggerplusplus import Logger

_logger = Logger(identifier="GetSerialNumber", follow_logger_manager_rules=True)


def get_all_serial_number() -> None:
    """Print the serial numbers of all detected serial ports."""
    ports = serial.tools.list_ports.comports()
    _logger.info(f"[USB_COM] Number of ports: {len(ports)}")
    for port in ports:
        _logger.info(f"[USB_COM] Serial Number: {port.serial_number}")


get_all_serial_number()
