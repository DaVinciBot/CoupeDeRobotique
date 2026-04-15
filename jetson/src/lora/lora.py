"""Module de communication LoRa (envoi + réception) pour DX LR01 via UART."""

import os
import threading
import time
from typing import Callable

import serial

HandlerFn = Callable[[list[str]], None]


class LoRa:
    """Communication bidirectionnelle via un module LoRa UART transparent."""

    def __init__(
        self,
        port: str,
        baudrate: int,
        min_send_interval: float = 1.0 / 15,
        tx_error_threshold: int = 5,
    ) -> None:
        self.port = port
        self.baudrate = baudrate
        self.serial: serial.Serial | None = None

        self._pending_data: str | None = None
        self._data_lock = threading.Lock()
        self._data_event = threading.Event()
        self._stop_event = threading.Event()

        self._tx_thread: threading.Thread | None = None
        self._rx_thread: threading.Thread | None = None
        self._min_send_interval = min_send_interval

        self._handlers: dict[int, HandlerFn] = {}
        self._rx_buffer = b""

        self._healthy = False
        self._tx_errors = 0
        self._tx_error_threshold = tx_error_threshold

    @property
    def is_healthy(self) -> bool:
        return self._healthy and self.serial is not None and self.serial.is_open

    def connect(self) -> None:
        """Ouvre le port série du module LoRa. Lève RuntimeError si indisponible."""
        if not os.path.exists(self.port):
            raise RuntimeError(
                f"Port LoRa introuvable: {self.port}. "
                "Vérifier le câblage du DX LR01 (pins 8/10 -> UART1 -> /dev/ttyTHS1) "
                "et que nvgetty est désactivé (sudo systemctl disable --now nvgetty)."
            )

        try:
            self.serial = serial.Serial(
                self.port,
                self.baudrate,
                timeout=0,
                write_timeout=0.5,
            )
        except serial.SerialException as e:
            raise RuntimeError(f"Échec ouverture LoRa {self.port}: {e}") from e

        time.sleep(1)

        if not self.serial.is_open:
            raise RuntimeError(f"Port LoRa {self.port} non ouvert après Serial()")

        try:
            self.serial.reset_input_buffer()
            self.serial.reset_output_buffer()
        except Exception as e:
            print(f"LoRa: flush buffers échoué: {e}")

        self._healthy = True
        self._tx_errors = 0
        print(f"LoRa connecté sur {self.port} @ {self.baudrate} baud")

    def start(self) -> None:
        """Démarre les threads d'envoi et de réception."""
        if self.serial is None or not self.serial.is_open:
            raise RuntimeError("LoRa.start() appelé sans connexion active")

        self._stop_event.clear()

        if not (self._tx_thread and self._tx_thread.is_alive()):
            self._tx_thread = threading.Thread(target=self._send_loop, daemon=True)
            self._tx_thread.start()

        if not (self._rx_thread and self._rx_thread.is_alive()):
            self._rx_thread = threading.Thread(target=self._recv_loop, daemon=True)
            self._rx_thread.start()

    def stop(self) -> None:
        """Arrête les threads TX et RX."""
        self._stop_event.set()
        self._data_event.set()

        for t in (self._tx_thread, self._rx_thread):
            if t and t.is_alive():
                t.join(timeout=2.0)

        self._tx_thread = None
        self._rx_thread = None

    def disconnect(self) -> None:
        """Ferme la connexion série."""
        self.stop()
        try:
            if self.serial and self.serial.is_open:
                self.serial.close()
        except Exception as e:
            print(f"Erreur déconnexion LoRa: {e}")
        self._healthy = False

    def queue_send(self, data: str) -> None:
        """File des données pour envoi (latest wins)."""
        with self._data_lock:
            self._pending_data = data
        self._data_event.set()

    def register_handler(self, cmd_num: int, callback: HandlerFn) -> None:
        """Enregistre un callback pour un N° de commande reçu.

        Le callback est appelé depuis le thread de réception LoRa avec la liste
        des arguments (strings). S'il doit modifier un état partagé avec la
        boucle principale, utiliser un verrou ou une queue côté appelant.
        """
        self._handlers[cmd_num] = callback

    def unregister_handler(self, cmd_num: int) -> None:
        self._handlers.pop(cmd_num, None)

    def _send_loop(self) -> None:
        while not self._stop_event.is_set():
            self._data_event.wait(timeout=0.5)
            self._data_event.clear()

            if self._stop_event.is_set():
                break

            with self._data_lock:
                data = self._pending_data
                self._pending_data = None

            if data is None:
                continue

            if not data.endswith("\n"):
                data += "\n"

            try:
                if self.serial and self.serial.is_open:
                    raw = data.encode("utf-8")
                    self.serial.write(raw)
                    self._tx_errors = 0
                    wire_time = len(raw) * 10.0 / self.baudrate
                    self._stop_event.wait(timeout=wire_time + self._min_send_interval)
            except Exception as e:
                self._tx_errors += 1
                print(f"Erreur envoi LoRa ({self._tx_errors}): {e}")
                if self._tx_errors >= self._tx_error_threshold:
                    self._healthy = False
                    print(
                        f"LoRa TX dégradé: {self._tx_errors} erreurs consécutives - "
                        "module probablement déconnecté"
                    )

    def _recv_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                if not (self.serial and self.serial.is_open):
                    self._stop_event.wait(timeout=0.1)
                    continue

                n = self.serial.in_waiting
                if n:
                    chunk = self.serial.read(n)
                    if chunk:
                        self._rx_buffer += chunk
                        while b"\n" in self._rx_buffer:
                            line, self._rx_buffer = self._rx_buffer.split(b"\n", 1)
                            self._dispatch(line)
                else:
                    self._stop_event.wait(timeout=0.02)
            except Exception as e:
                print(f"Erreur RX LoRa: {e}")
                self._stop_event.wait(timeout=0.1)

    def _dispatch(self, raw_line: bytes) -> None:
        try:
            line = raw_line.decode("utf-8", errors="replace").strip()
        except Exception as e:
            print(f"LoRa RX decode error: {e}")
            return

        if not line:
            return

        parts = line.split("|")
        try:
            cmd_num = int(parts[0])
        except ValueError:
            print(f"LoRa RX: trame sans N° de commande valide: {line!r}")
            return

        args = parts[1:]
        handler = self._handlers.get(cmd_num)
        if handler is None:
            print(f"LoRa RX: cmd N°{cmd_num} non gérée (args={args})")
            return

        try:
            handler(args)
        except Exception as e:
            print(f"LoRa RX: handler cmd N°{cmd_num} a levé {type(e).__name__}: {e}")
