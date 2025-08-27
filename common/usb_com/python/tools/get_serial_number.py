"""Utilities to list serial numbers of connected devices."""

import serial.tools.list_ports


def get_all_serial_number() -> None:
    """Print the serial numbers of all detected serial ports."""
    ports = serial.tools.list_ports.comports()
    print(f"Number of ports: {len(ports)}")
    for port in ports:
        print(f"Serial Number: {port.serial_number}")


get_all_serial_number()
