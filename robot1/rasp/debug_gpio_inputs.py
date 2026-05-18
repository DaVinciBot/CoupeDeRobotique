"""Standalone Raspberry Pi GPIO input diagnostics.

Run from the repository root:
    .venv/bin/python robot1/rasp/debug_gpio_inputs.py

By default this passively scans BCM GPIO pins 2..27 and prints pins whose
value changes. Move the tirette while it runs; the changing pin is the one to
check in config.json.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

REPO_ROOT = Path(__file__).resolve().parents[2]
for import_path in (
    REPO_ROOT / "common",
    REPO_ROOT / "robot1",
    REPO_ROOT / "robot1" / "rasp",
):
    sys.path.insert(0, str(import_path))


DEFAULT_BCM_PINS = tuple(range(2, 28))
RESERVED_BCM_PINS = (0, 1)
INPUT_MODES = ("input", "input_pullup", "input_pulldown")
BACKENDS = ("auto", "pinctrl", "raspi-gpio", "gpiozero")
RASPI_GPIO_RE = re.compile(r"GPIO\s+(?P<pin>\d+):.*level=(?P<value>[01])")
PINCTRL_RE = re.compile(r"(?P<pin>\d+):.*\|\s*(?P<value>hi|lo)\b")
BCM_TO_PHYSICAL = {
    2: 3,
    3: 5,
    4: 7,
    5: 29,
    6: 31,
    7: 26,
    8: 24,
    9: 21,
    10: 19,
    11: 23,
    12: 32,
    13: 33,
    14: 8,
    15: 10,
    16: 36,
    17: 11,
    18: 12,
    19: 35,
    20: 38,
    21: 40,
    22: 15,
    23: 16,
    24: 18,
    25: 22,
    26: 37,
    27: 13,
}


class Reader(Protocol):
    """Read digital values from GPIO pins."""

    name: str

    def setup(self, pin_numbers: list[int], mode: str, samples: int) -> dict[int, bool]:
        """Prepare pins when needed and return initial values."""

    def read(self, pin_number: int, samples: int) -> bool:
        """Read one pin value."""


@dataclass
class PinProbe:
    """Keep the last observed value for one pin."""

    pin_number: int
    value: bool


class CommandReader:
    """Read GPIO levels using a Raspberry Pi command-line tool."""

    def __init__(self, command: str, *, configure_pins: bool = False) -> None:
        """Initialize a command-backed reader."""
        self.name = command
        self._configure_pins = configure_pins
        self._pattern = PINCTRL_RE if command == "pinctrl" else RASPI_GPIO_RE

    def setup(self, pin_numbers: list[int], mode: str, samples: int) -> dict[int, bool]:
        """Return initial pin values without reserving GPIO lines."""
        if self._configure_pins:
            for pin_number in pin_numbers:
                self._set_input_mode(pin_number, mode)
            print(f"Backend: {self.name}; configured pins as {mode}.")
        else:
            print(f"Backend: {self.name} passive read. Mode '{mode}' is not applied.")
        return self._read_many(pin_numbers)

    def read(self, pin_number: int, samples: int) -> bool:
        """Read one pin through the command-line tool."""
        values = self._read_many([pin_number])
        return values[pin_number]

    def _read_many(self, pin_numbers: list[int]) -> dict[int, bool]:
        values: dict[int, bool] = {}
        for pin_number in pin_numbers:
            output = self._run(pin_number)
            match = self._pattern.search(output)
            if match is None:
                msg = f"Could not parse {self.name} output for GPIO {pin_number}: {output!r}"
                raise RuntimeError(msg)
            raw_value = match.group("value")
            values[pin_number] = raw_value in ("1", "hi")
        return values

    def _run(self, pin_number: int) -> str:
        command = [self.name, "get", str(pin_number)]
        completed = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
        return completed.stdout.strip()

    def _set_input_mode(self, pin_number: int, mode: str) -> None:
        if self.name == "pinctrl":
            pull = {"input": "pn", "input_pullup": "pu", "input_pulldown": "pd"}[mode]
        else:
            pull = {
                "input": "a0",
                "input_pullup": "pu",
                "input_pulldown": "pd",
            }[mode]
        subprocess.run(
            [self.name, "set", str(pin_number), "ip", pull],
            check=True,
            capture_output=True,
            text=True,
        )


class GpiozeroReader:
    """Read GPIO levels through the project's gpiozero wrapper."""

    name = "gpiozero"

    def __init__(self) -> None:
        """Initialize the reader."""
        self._pins: dict[int, object] = {}

    def setup(self, pin_numbers: list[int], mode: str, samples: int) -> dict[int, bool]:
        """Configure input pins through gpiozero."""
        from gpio import PIN

        values: dict[int, bool] = {}
        for pin_number in pin_numbers:
            pin = PIN(pin_number)
            pin.setup(mode)
            self._pins[pin_number] = pin
            values[pin_number] = bool(pin.safe_digital_read(samples))
        return values

    def read(self, pin_number: int, samples: int) -> bool:
        """Read one configured pin through gpiozero."""
        pin = self._pins[pin_number]
        return bool(pin.safe_digital_read(samples))


def parse_pin_list(value: str) -> list[int]:
    """Parse comma-separated pins and ranges, for example ``2,3,10-15``."""
    pins: list[int] = []
    for part in value.split(","):
        item = part.strip()
        if not item:
            continue
        if "-" in item:
            start_raw, end_raw = item.split("-", maxsplit=1)
            start = int(start_raw)
            end = int(end_raw)
            step = 1 if end >= start else -1
            pins.extend(range(start, end + step, step))
        else:
            pins.append(int(item))
    return list(dict.fromkeys(pins))


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""
    parser = argparse.ArgumentParser(
        description="Read Raspberry Pi GPIO inputs to identify the tirette pin.",
    )
    parser.add_argument(
        "--pins",
        type=parse_pin_list,
        default=list(DEFAULT_BCM_PINS),
        help="BCM pins to scan, comma/range format. Default: 2-27.",
    )
    parser.add_argument(
        "--include-reserved",
        action="store_true",
        help="Also scan BCM pins 0 and 1. These are usually reserved for HAT EEPROM.",
    )
    parser.add_argument(
        "--mode",
        choices=INPUT_MODES,
        default="input_pullup",
        help="Input setup mode for gpiozero backend. Default: input_pullup.",
    )
    parser.add_argument(
        "--backend",
        choices=BACKENDS,
        default="auto",
        help="GPIO read backend. Default: auto.",
    )
    parser.add_argument(
        "--configure",
        action="store_true",
        help=(
            "Configure scanned pins as inputs using --mode before reading. "
            "Use this only on known-safe GPIO pins."
        ),
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=0.05,
        help="Delay between reads in seconds. Default: 0.05.",
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=5,
        help="Samples per pin for majority read. Default: 5.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Print every pin at each loop instead of only changes.",
    )
    return parser


def select_readers(backend: str, *, configure_pins: bool) -> list[Reader]:
    """Select candidate GPIO readers."""
    readers: list[Reader] = []
    if backend in ("auto", "pinctrl") and shutil.which("pinctrl") is not None:
        readers.append(CommandReader("pinctrl", configure_pins=configure_pins))
    if backend in ("auto", "raspi-gpio") and shutil.which("raspi-gpio") is not None:
        readers.append(CommandReader("raspi-gpio", configure_pins=configure_pins))
    if backend in ("auto", "gpiozero"):
        readers.append(GpiozeroReader())

    if readers:
        return readers

    msg = f"No candidate for backend {backend!r} is available on this machine."
    raise RuntimeError(msg)


def setup_pins(
    reader: Reader,
    pin_numbers: list[int],
    mode: str,
    samples: int,
) -> list[PinProbe]:
    """Configure pins as needed and return readable probes."""
    probes: list[PinProbe] = []
    try:
        values = reader.setup(pin_numbers, mode, samples)
    except Exception as exc:  # noqa: BLE001 - debug script should report backend failure.
        print(f"Backend {reader.name} failed: {type(exc).__name__}: {exc}")
        return probes

    for pin_number, value in values.items():
        probes.append(PinProbe(pin_number=pin_number, value=value))
        print(f"{format_pin(pin_number)}: initial={format_value(value)}")
    return probes


def format_value(value: bool) -> str:
    """Return a compact digital-state label."""
    return "HIGH/1" if value else "LOW/0"


def format_pin(pin_number: int) -> str:
    """Return a label with BCM and physical header numbers."""
    physical = BCM_TO_PHYSICAL.get(pin_number)
    if physical is None:
        return f"GPIO {pin_number:>2}"
    return f"GPIO {pin_number:>2} / physical {physical:>2}"


def print_all(probes: list[PinProbe]) -> None:
    """Print one compact row with every current pin value."""
    states = "  ".join(
        f"{probe.pin_number:>2}:{'1' if probe.value else '0'}" for probe in probes
    )
    print(states)


def main() -> int:
    """Run the GPIO diagnostics loop."""
    args = build_parser().parse_args()
    if args.interval <= 0:
        print("--interval must be greater than 0.")
        return 2
    if args.samples <= 0:
        print("--samples must be greater than 0.")
        return 2

    pin_numbers = list(args.pins)
    if args.include_reserved:
        pin_numbers = list(RESERVED_BCM_PINS) + pin_numbers
    pin_numbers = list(dict.fromkeys(pin_numbers))

    print("GPIO numbering: BCM, not physical header pin numbers.")
    try:
        readers = select_readers(args.backend, configure_pins=args.configure)
    except Exception as exc:  # noqa: BLE001 - debug script should print simple failures.
        print(f"Could not select GPIO backend: {type(exc).__name__}: {exc}")
        return 1

    print(f"Backend candidates: {', '.join(reader.name for reader in readers)}")
    print(f"Mode: {args.mode}; interval: {args.interval}s; samples: {args.samples}")
    print("Press Ctrl+C to stop.\n")

    reader: Reader | None = None
    probes: list[PinProbe] = []
    for candidate_reader in readers:
        probes = setup_pins(candidate_reader, pin_numbers, args.mode, args.samples)
        if probes:
            reader = candidate_reader
            break
        if args.backend != "auto":
            break

    if not probes:
        print("\nNo GPIO pin could be read.")
        return 1

    if reader is None:
        print("\nNo GPIO backend could be initialized.")
        return 1

    print("\nNow move the tirette. Changed pins will be printed below.")
    if args.all:
        print_all(probes)

    try:
        while True:
            changed: list[tuple[int, bool, bool]] = []
            for probe in probes:
                try:
                    new_value = reader.read(probe.pin_number, args.samples)
                except Exception as exc:  # noqa: BLE001 - debug script should keep running.
                    print(
                        f"{format_pin(probe.pin_number)}: read failed "
                        f"({type(exc).__name__}: {exc})",
                    )
                    continue
                if new_value != probe.value:
                    changed.append((probe.pin_number, probe.value, new_value))
                    probe.value = new_value

            timestamp = time.strftime("%H:%M:%S")
            for pin_number, old_value, new_value in changed:
                print(
                    f"{timestamp} {format_pin(pin_number)}: "
                    f"{format_value(old_value)} -> {format_value(new_value)}",
                )
            if args.all:
                print_all(probes)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nStopped.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
