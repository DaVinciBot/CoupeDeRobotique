"""Rolling basis controller interfacing with the Teensy board."""

from __future__ import annotations

import struct
import time
from enum import Enum
from typing import TYPE_CHECKING, overload, override

from loggerplusplus import LogLevels, log

from a_config_loader import CONFIG
from controllers.rolling_basis.pids import PID, PidID
from geometry import OrientedPoint
from teensy import BaseComTeensy
from usb_com.python import Messages

from collections import deque

if TYPE_CHECKING:
    from loggerplusplus import Logger

    from navigation.trajectory_planner import TrajectoryPlanCommand


class RollingBasis(BaseComTeensy):
    """Represents the rolling basis of the robot.

    Inherits from Teensy to manage low-level communications and adds logic
    specific to the robot's state, PID configuration, and message messaging.
    """

    def __init__(
        self,
        logger: Logger,
        serial_number: int = CONFIG.ROLLING_BASIS_TEENSY_SER,
        vid: int = CONFIG.TEENSY_VID,
        pid: int = CONFIG.TEENSY_PID,
        baudrate: int = CONFIG.TEENSY_BAUDRATE,
        *,
        enable_crc: bool = CONFIG.TEENSY_CRC,
        enable_dummy: bool = CONFIG.ROLLING_BASIS_DUMMY,
    ) -> None:
        """Initializes the RollingBasis class.

        Args:
            logger (Logger): The logger instance for logging.
            serial_number (int, optional): The serial number of the Teensy.
                Defaults to CONFIG.ROLLING_BASIS_TEENSY_SER.
            vid (int, optional):
                The vendor ID of the Teensy. Defaults to CONFIG.TEENSY_VID.
            pid (int, optional):
                The product ID of the Teensy. Defaults to CONFIG.TEENSY_PID.
            baudrate (int, optional): The baud rate for serial communication.
                Defaults to CONFIG.TEENSY_BAUDRATE.
            enable_crc (bool, optional):
                Whether to enable CRC checks. Defaults to CONFIG.TEENSY_CRC.
            enable_dummy (bool, optional):
                Whether to enable dummy mode. Defaults to CONFIG.ROLLING_BASIS_DUMMY.
        """
        self.flag = True
        # Initialize the parent-BaseComTeensy class
        super().__init__(
            logger,
            serial_number,
            vid,
            pid,
            baudrate,
            enable_crc=enable_crc,
            enable_dummy=enable_dummy,
        )

        # Robot state
        self.odometrie: OrientedPoint = OrientedPoint((0.0, 0.0), 0.0)

        # PID controllers
        self.linear_velocity_pid: PID = PID(0.0, 0.0, 0.0)
        self.angular_velocity_pid: PID = PID(0.0, 0.0, 0.0)
        """
        This is used to match a handling function to a message type.
        add_callback can also be used.
        """
        # Register message handlers
        self.add_callback(self.rcv_print, Messages.PRINT.value)
        self.add_callback(self.rcv_unknown_msg, Messages.UNKNOWN_MSG_TYPE.value)
        self.add_callback(
            self.rcv_rolling_basis_state,
            Messages.UPDATE_ROLLING_BASIS.value,
        )

        time.sleep(0.01)  # Avoid overload
        self.reset_teensy_and_reinit()

        self._logs = []

        self.linear_velocity : float = 0
        self.angular_velocity : float = 0
        self.last_linear_error: float = 0.0
        self.last_angular_error: float = 0.0
        self.last_linear_correction: float = 0.0
        self.last_angular_correction: float = 0.0
        self.left_pwm: int = 0
        self.right_pwm: int = 0
        self.left_ticks: int = 0
        self.right_ticks: int = 0

        # On limite à 10 000 points (environ 8 min à 20Hz)
        self._logs = deque(maxlen=10000)

        # On stocke la dernière consigne envoyée pour l'associer au prochain feedback
        self._current_target_lin = 0.0
        self._current_target_ang = 0.0

    # region ====== Message Receiving Handlers ======

    def rcv_print(self, msg: bytes) -> None:
        """Handles PRINT messages from the Teensy.

        Args:
            msg (bytes): The received message bytes.
        """
        self._logger.info(
            f"[CTRL:RB:Teensy] {msg.decode('ascii', errors='ignore')}",
        )

    def rcv_rolling_basis_state(self, msg: bytes) -> None:
        # Format : 1 byte (cmd) + 13 doubles (d) + 2 int32 (i)
        # Taille totale attendue : 1 + (13 * 8) + (2 * 4) = 113 octets
        expected_size = 113

        if len(msg) < expected_size:
            return

        try:
            # On unpack à partir de l'index 1 (on saute l'ID du message)
            data = struct.unpack("<dddddddddddddii", msg[1:expected_size])

            # Mise à jour des objets
            self.odometrie = OrientedPoint((data[0], data[1]), data[2])
            self.linear_velocity = data[3]
            self.angular_velocity = data[4]
            self.last_linear_error = data[5]
            self.last_angular_error = data[6]
            self.last_linear_correction = data[7]
            self.last_angular_correction = data[8]
            self.left_pwm = data[9]
            self.right_pwm = data[10]

            # On utilise les targets venant du feedback pour plus de précision
            self._current_target_lin = data[11]
            self._current_target_ang = data[12]

            self.left_ticks = data[13]
            self.right_ticks = data[14]

            self._log_entry()

        except struct.error as e:
            self._logger.error(f"Erreur unpack: {e}")


    def rcv_unknown_msg(self, msg: bytes) -> None:
        """Handles unknown messages from the Teensy.

        Logs a warning indicating that the message type is not recognized.

        Args:
            msg (bytes): The received message bytes.
        """
        self._logger.warning(f"[CTRL:RB:Teensy] Unknown message type: {msg.hex()}")

    # endregion

    # region ====== Message Sending Methods ======

    class ControlMode(Enum):
        VELOCITY = 0
        POSITION = 1

    def reset_teensy_and_reinit(self, *, delay_s: float = 0.8) -> None:
        """Reset the Teensy and reinitialize rolling basis state."""
        self._logger.info("[CTRL:RB] Sending RESET_TEENSY")
        self.reset()
        time.sleep(delay_s)
        if not self.reconnect():
            return
        self.set_odometrie(OrientedPoint((0.0, 0.0), 0.0))
        msg = (
            Messages.SET_TARGET_VELOCITY.to_bytes()
            + struct.pack("<d", 0.0)
            + struct.pack("<d", 0.0)
        )
        self.send_bytes(msg)

    def set_control_mode(self, mode: ControlMode | int) -> None:
        """Set rolling basis control mode (velocity or position)."""
        mode_value = (
            mode.value if isinstance(mode, RollingBasis.ControlMode) else int(mode)
        )
        msg = Messages.SET_CONTROL_MODE.to_bytes() + bytes([mode_value])
        self.send_bytes(msg)

    # @log(param_logger="RollingBasis", log_level=LogLevels.INFO)
    def set_target_velocity(self, cmd: TrajectoryPlanCommand) -> None:
        """Envoi de consigne et mise à jour de la consigne locale."""
        self._current_target_lin = cmd.linear_speed
        self._current_target_ang = cmd.angular_speed

        msg = (
                Messages.SET_TARGET_VELOCITY.to_bytes()
                + struct.pack("<d", cmd.linear_speed)
                + struct.pack("<d", cmd.angular_speed)
        )
        self.send_bytes(msg)

    def set_target_pose(
        self,
        pose: OrientedPoint,
        linear_speed: float = 0.0,
        angular_speed: float = 0.0,
    ) -> None:
        """Send a command to set the target pose with optional feedforward."""
        msg = (
            Messages.SET_TARGET_POSE.to_bytes()
            + struct.pack("<d", pose.x)
            + struct.pack("<d", pose.y)
            + struct.pack("<d", pose.theta)
            + struct.pack("<d", linear_speed)
            + struct.pack("<d", angular_speed)
        )
        self.send_bytes(msg)

    @log(param_logger="RollingBasis", log_level=LogLevels.INFO)
    def set_odometrie(self, odometrie: OrientedPoint) -> None:
        """Sends a message to set the odometrie of the rolling basis.

        Args:
            odometrie (OrientedPoint): The new odometrie values.

        Raises:
            ValueError: If odometrie.theta is None.
        """
        if odometrie.theta is None:
            msg = (
                f"Odometrie theta must be defined, got None at "
                f"position ({odometrie.x}, {odometrie.y})"
            )
            raise ValueError(msg)

        msg = (
            Messages.SET_ODOMETRIE.to_bytes()
            + struct.pack("<d", odometrie.x)
            + struct.pack("<d", odometrie.y)
            + struct.pack("<d", odometrie.theta)
        )

        self.send_bytes(msg)

    @log(
        param_logger="RollingBasis",
        log_level=LogLevels.INFO,
    )
    def _send_pid(self, pid_id: int, pid: PID) -> None:
        """Internal method to send PID configuration data to the Teensy.

        Args:
            pid_id (int): The identifier for the PID controller.
            pid (PID): The PID controller parameters.
        """
        msg = Messages.SET_PID.to_bytes() + pid_id.to_bytes() + pid.to_bytes()
        self.send_bytes(msg)

    # endregion

    # region ====== PID Configuration Methods ======

    @staticmethod
    def _load_pid(
        *args: float | dict[str, float],
        **kwargs: float,
    ) -> PID:
        """Load the PID values.

        Args:
            *args (float | dict[str, float]): Either three floats (kp, ki, kd) or a
                single dictionary with keys 'kp', 'ki', 'kd'.
            **kwargs (float): Keyword arguments mapping PID fields to values.

        Returns:
            PID: The configured PID instance.

        Raises:
            ValueError: If the arguments do not match any expected format.
        """
        if len(args) == 3 and all(isinstance(arg, float) for arg in args):  # noqa: PLR2004
            pid = PID(*args)  # pyright: ignore[reportArgumentType] args are all float
        elif len(args) == 1 and isinstance(args[0], dict):
            pid = PID.from_dict(args[0])
        elif kwargs:
            pid = PID.from_dict(kwargs)
        else:
            msg = "Invalid arguments for PID configuration."
            raise ValueError(msg)
        return pid

    @overload
    def set_linear_velocity_pid(self, *args: float) -> None: ...

    @overload
    def set_linear_velocity_pid(self, pid_values: dict[str, float]) -> None: ...

    @overload
    def set_linear_velocity_pid(self, kp: float, ki: float, kd: float) -> None: ...

    def set_linear_velocity_pid(
        self,
        *args: float | dict[str, float],
        **kwargs: float,
    ) -> None:
        """Configure the PID values for linear position control.

        Overloads:
            - set_linear_velocity_pid(float, float, float) → None
            - set_linear_velocity_pid(dict[str, float]) → None
            - set_linear_velocity_pid(kp=float, ki=float, kd=float) → None

        Args:
            *args (float | dict[str, float]): Either three floats (kp, ki, kd) or a
                single dictionary with keys 'kp', 'ki', 'kd'.
            **kwargs (float): Keyword arguments mapping PID fields to values.
        """
        try:
            pid = self._load_pid(*args, **kwargs)
            self.linear_velocity_pid = pid
            self._send_pid(PidID.LINEAR_VELOCITY.value, pid)
        except (ValueError, TypeError) as e:
            self._logger.error(f"[CTRL:RB] Failed to set linear velocity PID: {e}")

    @overload
    def set_angular_velocity_pid(self, *args: float) -> None: ...

    @overload
    def set_angular_velocity_pid(self, pid_values: dict[str, float]) -> None: ...

    @overload
    def set_angular_velocity_pid(self, kp: float, ki: float, kd: float) -> None: ...

    def set_angular_velocity_pid(
        self,
        *args: float | dict[str, float],
        **kwargs: float,
    ) -> None:
        """Configure the PID values for angular velocity control.

        Overloads:
            - set_angular_velocity_pid(float, float, float) → None
            - set_angular_velocity_pid(dict[str, float]) → None
            - set_angular_velocity_pid(kp=float, ki=float, kd=float) → None

        Args:
            *args (float | dict[str, float]): Either three floats (kp, ki, kd) or
                a single dictionary with keys 'kp', 'ki', 'kd'.
            **kwargs (float): Keyword arguments mapping PID fields to values.
        """
        try:
            pid = self._load_pid(*args, **kwargs)
            self.angular_velocity_pid = pid
            self._send_pid(PidID.ANGULAR_VELOCITY.value, pid)
        except (ValueError, TypeError) as e:
            self._logger.error(f"[CTRL:RB] Failed to set angular velocity PID: {e}")

    def set_pids(
        self,
        linear_velocity_pid: dict[str, float],
        angular_velocity_pid: dict[str, float],
    ) -> None:
        """Configure all PID controllers using dictionaries for each.

        Args:
            linear_velocity_pid (dict[str, float]):
                PID configuration for linear velocity.
            angular_velocity_pid (dict[str, float]):
                PID configuration for angular velocity.
        """
        self.set_linear_velocity_pid(**linear_velocity_pid)
        time.sleep(0.1)  # Ensure the Teensy has time to process the first PID
        self.set_angular_velocity_pid(**angular_velocity_pid)
        time.sleep(0.1)  # Ensure the Teensy has time to process the second PID

    def initialize_pids(self) -> None:
        """Initialize PID controllers from the configuration."""
        try:
            self.set_pids(
                linear_velocity_pid=CONFIG.ROLLING_BASIS_PIDS_LINEAR_VELOCITY,
                angular_velocity_pid=CONFIG.ROLLING_BASIS_PIDS_ANGULAR_VELOCITY,
            )
        except (ValueError, TypeError) as e:
            self._logger.error(f"[CTRL:RB] Failed to initialize PIDs: {e}")

    # endregion

    def _log_entry(self) -> None:
        """Enregistre les données synchronisées avec le feedback du Teensy."""
        entry = {
            "time": time.time(),
            "target_lin": self._current_target_lin,
            "target_ang": self._current_target_ang,
            "actual_x": self.odometrie.x,
            "actual_y": self.odometrie.y,
            "actual_theta": self.odometrie.theta,
            "err_lin": self.last_linear_error,
            "err_ang": self.last_angular_error,
            "corr_lin": self.last_linear_correction,
            "corr_ang": self.last_angular_correction,
            "left_pwm": self.left_pwm,
            "right_pwm": self.right_pwm,
            "left_ticks": self.left_ticks,
            "right_ticks": self.right_ticks,
        }
        self._logs.append(entry)

    def plot_logs(self):
        """Génère un dashboard complet pour le diagnostic du comportement du robot."""
        if not self._logs:
            self._logger.warning("[CTRL:RB] Aucun log à tracer.")
            return

        import matplotlib.pyplot as plt
        import numpy as np

        # Conversion en dictionnaire de listes pour manipulation facile
        # On utilise list() car self._logs est une deque
        data = {k: [d[k] for d in self._logs] for k in self._logs[0].keys()}

        t0 = data["time"][0]
        times = np.array(data["time"]) - t0

        # Création de la figure avec une grille personnalisée
        fig, axs = plt.subplots(4, 2, figsize=(15, 12), sharex=True)
        fig.suptitle(f"Diagnostic Rolling Basis - {time.strftime('%H:%M:%S')}", fontsize=16)

        # --- 1. VITESSE LINÉAIRE (Target vs Actual) ---
        axs[0, 0].plot(times, data["target_lin"], 'r--', label="Consigne", alpha=0.8)
        # Note: Assurez-vous que 'actual_lin' est bien envoyé par la Teensy
        # Si non, on peut utiliser une approximation ou juste l'erreur.
        axs[0, 0].set_title("Vitesse Linéaire (cm/s)")
        axs[0, 0].legend()
        axs[0, 0].grid(True, which='both', linestyle='--', alpha=0.5)

        # --- 2. VITESSE ANGULAIRE (Target vs Actual) ---
        axs[0, 1].plot(times, data["target_ang"], 'r--', label="Consigne", alpha=0.8)
        axs[0, 1].set_title("Vitesse Angulaire (rad/s)")
        axs[0, 1].legend()
        axs[0, 1].grid(True, linestyle='--', alpha=0.5)

        # --- 3. ERREURS PID ---
        axs[1, 0].plot(times, data["err_lin"], color='tab:orange', label="Erreur Lin")
        axs[1, 0].set_title("Erreur de suivi Linéaire")
        axs[1, 0].axhline(0, color='black', lw=1)
        axs[1, 0].legend()
        axs[1, 0].grid(True)

        axs[1, 1].plot(times, data["err_ang"], color='tab:purple', label="Erreur Ang")
        axs[1, 1].set_title("Erreur de suivi Angulaire")
        axs[1, 1].axhline(0, color='black', lw=1)
        axs[1, 1].legend()
        axs[1, 1].grid(True)

        # --- 4. SORTIES PID (CORRECTIONS) ---
        axs[2, 0].plot(times, data["corr_lin"], color='tab:green', label="Correction Lin")
        axs[2, 0].set_title("Sortie PID Linéaire")
        axs[2, 0].legend()
        axs[2, 0].grid(True)

        axs[2, 1].plot(times, data["corr_ang"], color='tab:olive', label="Correction Ang")
        axs[2, 1].set_title("Sortie PID Angulaire")
        axs[2, 1].legend()
        axs[2, 1].grid(True)

        # --- 5.

    # region ====== Built-in methods ======

    @override
    def __eq__(self, other: object) -> bool:
        """Check equality between two RollingBasis instances.

        Args:
            other (object): The other object to compare against.

        Returns:
            bool: ``True`` if the objects are equal, ``False`` otherwise.
        """
        if not isinstance(other, RollingBasis):
            return NotImplemented
        return (
            self.odometrie == other.odometrie
            and self.linear_velocity_pid == other.linear_velocity_pid
            and self.angular_velocity_pid == other.angular_velocity_pid
        )

    @override
    def __ne__(self, other: object) -> bool:
        """Check inequality between two RollingBasis instances.

        Args:
            other (object): The other object to compare against.

        Returns:
            bool: ``True`` if the objects are not equal, ``False`` otherwise.
        """
        return not self.__eq__(other)

    @override
    def __hash__(self) -> int:
        """Return a hash based on object identity.

        Returns:
            int: The hash value of the object.
        """
        return object.__hash__(self)

    # endregion
