from config_loader import CONFIG

# ====== Standard Library Imports ======
import struct
import time

# ====== Third-party library imports ======
from loggerplusplus import Logger, log, LogLevels

# ====== Local Library Imports ======
from geometry import OrientedPoint
from usb_com.python import Messages
from teensy import BaseComTeensy

# ====== Internal Project Imports ======
from controllers.rolling_basis.pids import PID, PID_ID
import matplotlib.pyplot as plt

class AsservissementRollingBasis(BaseComTeensy):
    """
    Represents the rolling basis of the robot.

    Inherits from Teensy to manage low-level communications and adds logic specific to the robot's state,
    PID configuration, and message messaging. Automatically logs target vs actual odometry on each send.
    """

    def __init__(
        self,
        logger: Logger,
        serial_number=CONFIG.ROLLING_BASIS_TEENSY_SER,
        vid=CONFIG.TEENSY_VID,
        pid=CONFIG.TEENSY_PID,
        baudrate=CONFIG.TEENSY_BAUDRATE,
        enable_crc=CONFIG.TEENSY_CRC,
        enable_dummy=CONFIG.TEENSY_DUMMY,
    ):
        # Initialize state and log storage
        self.logger = logger
        self.odometrie: OrientedPoint = OrientedPoint((0.0, 0.0), 0.0)
        self._last_target: OrientedPoint = OrientedPoint((0.0, 0.0), 0.0)
        self._logs: list[dict] = []  # store dicts of time, target, actual

        # Initialize parent
        super().__init__(
            logger, serial_number, vid, pid, baudrate, enable_crc, enable_dummy
        )

        # PID controllers
        self.linear_position_pid: PID = PID(0.0, 0.0, 0.0)
        self.angular_position_pid: PID = PID(0.0, 0.0, 0.0)

        # Register message handlers
        self.add_callback(self.rcv_print, Messages.PRINT.value)
        self.add_callback(self.rcv_unknown_msg, Messages.UNKNOWN_MSG_TYPE.value)
        self.add_callback(
            self.rcv_rolling_basis_state, Messages.UPDATE_ROLLING_BASIS.value
        )

        self._initialize_pids()

    ####################################
    # Message Receiving Handlers       #
    ####################################
    def rcv_print(self, msg: bytes):
        self.logger.info(
            "Teensy Rolling Basis says: " + msg.decode("ascii", errors="ignore")
        )

    def rcv_rolling_basis_state(self, msg: bytes):
        # Unpack new odometry
        self.odometrie = OrientedPoint(
            (struct.unpack("<d", msg[0:8])[0], struct.unpack("<d", msg[8:16])[0]),
            struct.unpack("<d", msg[16:24])[0],
        )
        # After receiving actual state, log entry
        self._log_entry()

    def rcv_unknown_msg(self, msg: bytes):
        self.logger.warning(f"Teensy Motors does not know the message {msg.hex()}")

    ####################################
    # Message Sending Methods          #
    ####################################
    def set_target_position(
        self,
        target_position: OrientedPoint,
    ) -> None:
        """
        Sends a message to set the target position of the rolling basis and logs the previous state.
        """
        # Store for logging
        self._last_target = target_position

        # Build and send message
        msg = (
            Messages.SET_TARGET_POSITION.to_bytes()
            + struct.pack("<d", target_position.x)
            + struct.pack("<d", target_position.y)
            + struct.pack("<d", target_position.theta)
        )
        self.send_bytes(msg)

        ####################################
        # Plotting Method                  #
        ####################################

    def plot_logs(self) -> None:
        """
        Plot target vs actual odometry for X, Y, and Theta using stored logs.
        Ensures all series have the same length before plotting.
        """
        logs = self.get_logs()
        if not logs:
            self.logger.warning("No logs to plot. Ensure that set_target_position() has been called.")
            return

        # Normalize time
        t0 = logs[0]['time']
        # Determine number of entries
        n = len(logs)

        # Build each series by index to guarantee equal length
        times = [(logs[i]['time'] - t0) for i in range(n)]
        target_x = [logs[i]['target_x'] for i in range(n)]
        actual_x = [logs[i]['actual_x'] for i in range(n)]
        target_y = [logs[i]['target_y'] for i in range(n)]
        actual_y = [logs[i]['actual_y'] for i in range(n)]
        target_th = [logs[i]['target_theta'] for i in range(n)]
        actual_th = [logs[i]['actual_theta'] for i in range(n)]

        # Optional sanity check
        assert all(len(lst) == n for lst in (times, target_x, actual_x, target_y, actual_y, target_th, actual_th)), \
            f"Inconsistent log lengths: {[len(lst) for lst in (times, target_x, actual_x, target_y, actual_y, target_th, actual_th)]}"

        # Plot
        fig, axs = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

        axs[0].plot(times, target_x, label='Consigne X')
        axs[0].plot(times, actual_x, label='Réel X')
        axs[0].set_ylabel('X (cm)')
        axs[0].legend()

        axs[1].plot(times, target_y, label='Consigne Y')
        axs[1].plot(times, actual_y, label='Réel Y')
        axs[1].set_ylabel('Y (cm)')
        axs[1].legend()

        axs[2].plot(times, target_th, label='Consigne θ')
        axs[2].plot(times, actual_th, label='Réel θ')
        axs[2].set_ylabel('θ (rad)')
        axs[2].set_xlabel('Temps (s)')
        axs[2].legend()

        plt.tight_layout()
        plt.show()

    ####################################
    # Logging Methods                  #
    ####################################
    def _log_entry(self) -> None:
        """
        Internal: record timestamp, last target, and latest odometry.
        """
        entry = {
            "time": time.time(),
            "target_x": self._last_target.x,
            "target_y": self._last_target.y,
            "target_theta": self._last_target.theta,
            "actual_x": self.odometrie.x,
            "actual_y": self.odometrie.y,
            "actual_theta": self.odometrie.theta,
        }
        self._logs.append(entry)

    def get_logs(self) -> list[dict]:
        """
        Returns the recorded log entries.
        Each entry is a dict with keys: time, target_x, target_y, target_theta,
        actual_x, actual_y, actual_theta.
        """
        return self._logs

    def clear_logs(self) -> None:
        """Clears the stored log entries."""
        self._logs.clear()

    @log(param_logger="RollingBasis", log_level=LogLevels.INFO)
    def set_odometrie(self, odometrie: OrientedPoint) -> None:
        """
        Sends a message to set the odometrie of the rolling basis.

        Args:
            odometrie (OrientedPoint): The new odometrie values.
        """
        msg = (
            Messages.SET_ODOMETRIE.to_bytes()
            + struct.pack("<d", odometrie.x)
            + struct.pack("<d", odometrie.y)
            + struct.pack("<d", odometrie.theta)
        )
        self.send_bytes(msg)

    ####################################
    # PID Configuration Methods        #
    ####################################
    @log(
        param_logger="RollingBasis",
        log_level=LogLevels.INFO,
    )
    def _send_pid(self, pid_id: int, pid: PID) -> None:
        """
        Internal method to send PID configuration data to the Teensy.

        Args:
            pid_id (int): The identifier for the PID controller.
            pid (PID): The PID controller parameters.
        """
        msg = Messages.SET_PID.to_bytes() + pid_id.to_bytes() + pid.to_bytes()
        self.send_bytes(msg)
    def set_linear_position_pid(self, *args, **kwargs) -> None:
        """
        Configure the PID values for linear position control.

        Accepts either three positional arguments (kp, ki, kd),
        a single dictionary, or keyword arguments.
        """
        try:
            if len(args) == 3:
                pid = PID(*args)
            elif len(args) == 1 and isinstance(args[0], dict):
                pid = PID.from_dict(args[0])
            elif kwargs:
                pid = PID.from_dict(kwargs)
            else:
                raise ValueError(
                    "Invalid arguments for linear position PID configuration."
                )
            self.linear_position_pid = pid
            self._send_pid(PID_ID.LINEAR_POSITION.value, pid)
        except Exception as e:
            self.logger.error(f"Failed to set linear position PID: {e}")

    def set_angular_position_pid(self, *args, **kwargs) -> None:
        """
        Configure the PID values for angular position control.

        Accepts either three positional arguments (kp, ki, kd),
        a single dictionary, or keyword arguments.
        """
        try:
            if len(args) == 3:
                pid = PID(*args)
            elif len(args) == 1 and isinstance(args[0], dict):
                pid = PID.from_dict(args[0])
            elif kwargs:
                pid = PID.from_dict(kwargs)
            else:
                raise ValueError(
                    "Invalid arguments for angular position PID configuration."
                )
            self.angular_position_pid = pid
            self._send_pid(PID_ID.ANGULAR_POSITION.value, pid)
        except Exception as e:
            self.logger.error(f"Failed to set angular position PID: {e}")

    def set_pids(
        self,
        linear_position_pid: dict[str, float],
        angular_position_pid: dict[str, float],
    ) -> None:
        """
        Configure all PID controllers using dictionaries for each.
        """
        self.set_linear_position_pid(**linear_position_pid)
        time.sleep(0.1)  # Ensure the Teensy has time to process the first PID
        self.set_angular_position_pid(**angular_position_pid)
        time.sleep(0.1)  # Ensure the Teensy has time to process the second PID

    def _initialize_pids(self) -> None:
        """
        Initialize PID controllers from the configuration.
        """
        try:
            self.set_pids(
                linear_position_pid=CONFIG.ROLLING_BASIS_PIDS_LINEAR_POSITION,
                angular_position_pid=CONFIG.ROLLING_BASIS_PIDS_ANGULAR_POSITION,
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize PIDs: {e}")

    ####################################
    # Equality Comparison              #
    ####################################
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AsservissementRollingBasis):
            return NotImplemented
        return (
            self.odometrie == other.odometrie
            and self.linear_position_pid == other.linear_position_pid
            and self.angular_position_pid == other.angular_position_pid
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
