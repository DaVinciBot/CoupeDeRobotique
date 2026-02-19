"""Module d'envoi de données via LoRa."""

import threading
import time

import serial


class LoRa:
    """Envoi de données via LoRa."""

    def __init__(
        self,
        port: str,
        baudrate: int,
        min_send_interval: float = 1.0 / 15,
    ) -> None:
        """Initialise la connexion LoRa."""
        self.port = port
        self.baudrate = baudrate
        self.serial = None
        self._pending_data = None
        self._data_lock = threading.Lock()
        self._data_event = threading.Event()
        self._stop_event = threading.Event()
        self._thread = None
        self._min_send_interval = min_send_interval

    def connect(self) -> None:
        """Établit la connexion série."""
        try:
            self.serial = serial.Serial(self.port, self.baudrate, timeout=0)
            time.sleep(1)
            print(f"Connecté LoRa sur {self.port} à {self.baudrate} baud")
        except Exception as e:
            print(f"Erreur connexion LoRa: {e}")

    def start(self) -> None:
        """Démarre le thread d'envoi."""
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._send_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Arrête le thread d'envoi."""
        self._stop_event.set()
        self._data_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        self._thread = None

    def disconnect(self) -> None:
        """Ferme la connexion série."""
        self.stop()
        try:
            if self.serial and self.serial.is_open:
                self.serial.close()
        except Exception as e:
            print(f"Erreur déconnexion LoRa: {e}")

    def queue_send(self, data: str) -> None:
        """File des données pour envoi (latest wins)."""
        with self._data_lock:
            self._pending_data = data
        self._data_event.set()

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

            try:
                if self.serial and self.serial.is_open:
                    raw = data.encode("utf-8")
                    self.serial.write(raw)
                    wire_time = len(raw) * 10.0 / self.baudrate
                    self._stop_event.wait(timeout=wire_time + self._min_send_interval)
            except Exception as e:
                print(f"Erreur envoi LoRa: {e}")
