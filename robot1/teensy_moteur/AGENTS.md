# Repository Guidelines

## Project Structure & Module Organization
- `platformio.ini`: single environment `teensy41` using Arduino framework and the shared `com` dependency (`../../common/usb_com/cpp` symlink).
- `src/main.cpp`: runtime entrypoint wiring Rolling_Basis motion control, communication callbacks, and timer interrupt handling.
- `include/config.h`: pinout, PID gains, and frequency constants; treat it as the source of truth for hardware setup.
- `lib/rolling_basis`, `lib/motors_driver`, `lib/pid`, `lib/kf1d`: robot motion, motor driver, PID, and Kalman filter logic; add new modules as separate folders under `lib/`.
- `.pio/`: PlatformIO build artifacts (do not edit); `.vscode/`: local editor tasks/settings.

## Build, Test, and Development Commands
- `pio run`: build the firmware for Teensy 4.1 (environment `teensy41`).
- `pio run -t upload --upload-port <port>`: flash the board; ensure the correct COM port is provided.
- `pio device monitor -b <baud>` (default matches `BAUDRATE` in `config.h`): open the serial monitor for telemetry and logs.
- `pio run -t clean`: remove build outputs when switching toolchains or after board definition changes.

## Coding Style & Naming Conventions
- `.clang-format` (Chromium style) with 4-space indentation is authoritative; run your formatter before committing.
- Prefer descriptive snake_case for functions/variables (`left_motor_read_encoder`), UPPER_SNAKE_CASE for constants/macros (`ASSERVISSEMENT_FREQUENCY`).
- Keep ISR-safe code in interrupt handlers (no dynamic allocation or blocking I/O); confine configuration changes to `config.h`.
- Maintain small, focused callbacks and keep shared state updates inside `ATOMIC` sections where contention is possible.

## Testing Guidelines
- There is no test suite yet. If you add tests, place them under `test/` and run with `pio test`.
- For manual validation, build then monitor serial output to verify odometry updates and PID responses; document bench setups in PRs when hardware behavior changes.

## Commit & Pull Request Guidelines
- Commit history favors short, imperative summaries with optional emoji prefixes (e.g., `🚑 fix ...`, `🌟 add ...`); keep messages focused on the change.
- In PRs, include: purpose, affected modules (`rolling_basis`, PID, comms), any hardware assumptions (pinouts, baud), and before/after behavior. Attach logs or monitor snippets when relevant.
- Link to tickets/issues when available and call out breaking changes (protocol messages, pin remaps, timing-sensitive adjustments).

## Security & Configuration Tips
- Treat `config.h` as the only writable source for pin mappings and gains; avoid hardcoding magic numbers elsewhere.
- The `RESET_TEENSY` callback reboots the board; gate new reset-like functionality behind explicit message IDs and sanity checks.
