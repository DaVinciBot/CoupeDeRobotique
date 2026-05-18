"""Standalone LiDAR diagnostics.

Run from the repository root:
    .venv/bin/python robot1/rasp/debug_lidar.py
"""

from __future__ import annotations

import importlib
import time
from collections.abc import Iterable

import serial
import serial.tools.list_ports
import usb.core

SICK_USB_VID = 0x19A2
SICK_USB_PID = 0x5001
SERIAL_BAUDRATES = (9600, 19200, 38400, 57600, 115200, 230400, 500000, 1000000)
SERIAL_FORMATS = (
    ("8N1", serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE),
    ("8E1", serial.EIGHTBITS, serial.PARITY_EVEN, serial.STOPBITS_ONE),
    ("7E1", serial.SEVENBITS, serial.PARITY_EVEN, serial.STOPBITS_ONE),
)
COLA_COMMANDS = (
    "sRN DeviceIdent",
    "sRN FirmwareVersion",
    "sRN LMPscancfg",
    "sRN LMDscandata",
)


def print_usb_devices() -> None:
    """List USB devices visible through pyusb."""
    print("== USB devices visible through pyusb ==")
    try:
        devices = list(usb.core.find(find_all=True))
    except Exception as exc:
        print(f"pyusb device listing failed: {type(exc).__name__}: {exc}")
        return

    if not devices:
        print("No USB devices found by pyusb.")
        return

    for dev in devices:
        marker = (
            " <- expected SICK LiDAR"
            if (dev.idVendor, dev.idProduct)
            == (
                SICK_USB_VID,
                SICK_USB_PID,
            )
            else ""
        )
        print(f"{dev.idVendor:04x}:{dev.idProduct:04x}{marker}")


def print_serial_ports() -> list[serial.tools.list_ports.ListPortInfo]:
    """List serial ports visible through pyserial."""
    print("\n== Serial ports visible through pyserial ==")
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("No serial ports found.")
        return ports

    for port in ports:
        print(
            f"{port.device}: vid={port.vid!r} pid={port.pid!r} "
            f"serial={port.serial_number!r} desc={port.description!r} "
            f"hwid={port.hwid!r}",
        )
    return ports


def test_pysicktim() -> None:
    """Test the current robot LiDAR dependency."""
    print("\n== pysicktim backend ==")
    try:
        pysicktim = importlib.import_module("pysicktim")
    except Exception as exc:
        print(f"pysicktim import failed: {type(exc).__name__}: {exc}")
        return

    lidar = getattr(pysicktim, "lidar", None)
    print(f"pysicktim.lidar = {lidar!r}")
    if lidar is None:
        print("pysicktim did not find the USB SICK LiDAR.")
        return

    try:
        pysicktim.scan()
    except Exception as exc:
        print(f"pysicktim scan failed: {type(exc).__name__}: {exc}")
        return

    distances = getattr(pysicktim.scan, "distances", None)
    print(f"pysicktim scan distances: {len(distances or [])} values")


def read_available(ser: serial.Serial, timeout_s: float = 0.4) -> bytes:
    """Read all bytes available for a short time window."""
    end = time.monotonic() + timeout_s
    chunks: list[bytes] = []
    while time.monotonic() < end:
        waiting = ser.in_waiting
        if waiting:
            chunks.append(ser.read(waiting))
            end = time.monotonic() + timeout_s
        time.sleep(0.02)
    return b"".join(chunks)


def cola_frames(command: str) -> Iterable[bytes]:
    """Return common CoLa serial frame variants for one command."""
    raw = command.encode("ascii")
    yield b"\x02" + raw + b"\x03"
    yield b"\x02" + raw + b"\x03\x00"
    yield raw + b"\n"
    yield raw + b"\r\n"
    yield raw + b"\x00"


def format_response(response: bytes) -> str:
    """Render bytes as text when possible, with a hex fallback."""
    text = response.decode("ascii", errors="replace")
    hex_preview = response[:80].hex(" ")
    return f"text={text[:300]!r} hex={hex_preview}"


def test_serial_cola(port: str) -> None:
    """Try CoLa ASCII commands on a serial port."""
    print(f"\n== Serial CoLa probe on {port} ==")
    for baudrate in SERIAL_BAUDRATES:
        for format_name, bytesize, parity, stopbits in SERIAL_FORMATS:
            settings = f"baud={baudrate} format={format_name}"
            try:
                with serial.Serial(
                    port,
                    baudrate=baudrate,
                    bytesize=bytesize,
                    parity=parity,
                    stopbits=stopbits,
                    timeout=0.2,
                ) as ser:
                    ser.dtr = True
                    ser.rts = True
                    time.sleep(0.05)
                    passive = read_available(ser, timeout_s=0.8)
                    if passive:
                        print(f"{port} {settings} passive {format_response(passive)}")

                    ser.reset_input_buffer()
                    ser.reset_output_buffer()
                    for command in COLA_COMMANDS:
                        for frame in cola_frames(command):
                            ser.write(frame)
                            ser.flush()
                            response = read_available(ser)
                            if response:
                                print(
                                    f"{port} {settings} command={frame!r} "
                                    f"{format_response(response)}",
                                )
                                return
                    print(f"{port} {settings}: no CoLa response")
            except Exception as exc:
                print(f"{port} {settings}: {type(exc).__name__}: {exc}")


def sniff_serial(port: str) -> None:
    """Read serial data without sending commands."""
    print(f"\n== Passive serial sniff on {port} ==")
    for baudrate in SERIAL_BAUDRATES:
        try:
            with serial.Serial(port, baudrate=baudrate, timeout=0.2) as ser:
                ser.reset_input_buffer()
                response = read_available(ser, timeout_s=3.0)
                if response:
                    print(f"{port} baud={baudrate} passive {format_response(response)}")
                    return
                print(f"{port} baud={baudrate}: no passive data")
        except Exception as exc:
            print(f"{port} baud={baudrate}: {type(exc).__name__}: {exc}")


def main() -> None:
    """Run all diagnostics."""
    print_usb_devices()
    ports = print_serial_ports()
    test_pysicktim()

    for port in ports:
        if port.device.startswith("/dev/ttyUSB"):
            sniff_serial(port.device)
            test_serial_cola(port.device)


if __name__ == "__main__":
    main()
