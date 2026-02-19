"""Module d'envoi de données via LoRa."""

import threading
import time

import serial


class LoRa:
    """Classe d'envoi de données via LoRa."""

    def __init__(
        self, port: str, baudrate: int, min_send_interval: float = 1.0 / 15,
    ) -> None:
        """Initialise la classe LoRa.

        Args:
            port: Port série de la carte LoRa
            baudrate: Baudrate de la communication série
            min_send_interval: Intervalle minimum entre deux envois (secondes)
        """
        self.port = port
        self.baudrate = baudrate
        self.serial = None

        # Threading state for background sending
        self._pending_data = None
        self._data_lock = threading.Lock()
        self._data_event = threading.Event()
        self._stop_event = threading.Event()
        self._thread = None
        self._min_send_interval = min_send_interval

    def connect(self) -> None:
        """Établit la connexion série avec la carte LoRa."""
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1,
                rtscts=False,
                xonxoff=False,
            )
            time.sleep(1)
            print(f"✅ Connecté à la carte LoRa sur {self.port} à {self.baudrate} baud")
        except Exception as e:
            print(f"Erreur de connexion à la carte LoRa: {e}")

    def start(self) -> None:
        """Démarre le thread d'envoi en arrière-plan."""
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._send_loop, daemon=True)
        self._thread.start()
        print("📡 Thread d'envoi LoRa démarré")

    def stop(self) -> None:
        """Arrête proprement le thread d'envoi."""
        self._stop_event.set()
        self._data_event.set()  # Réveille le thread pour qu'il voie le signal d'arrêt
        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        self._thread = None

    def disconnect(self) -> None:
        """Ferme la connexion série avec la carte LoRa."""
        self.stop()
        try:
            if self.serial and self.serial.is_open:
                self.serial.close()
                print("✅ Déconnecté de la carte LoRa")
        except Exception as e:
            print(f"Erreur de déconnexion de la carte LoRa: {e}")

    def queue_send(self, data: str) -> None:
        """File des données pour envoi en arrière-plan (non bloquant).

        Stratégie 'latest wins': si des données sont déjà en attente,
        elles sont remplacées par les nouvelles.

        Args:
            data: Données à envoyer
        """
        with self._data_lock:
            self._pending_data = data
        self._data_event.set()

    def send(self, data: str) -> None:
        """Envoie des données via LoRa.

        Args:
            data: Données à envoyer
        """
        serial_data = data.encode("utf-8")
        if self.serial and self.serial.is_open:
            self.serial.write(serial_data)
            self.serial.flush()
        else:
            print(
                "Erreur: Le module LoRa n'est pas connecté.",
            )

    def _send_loop(self) -> None:
        """Boucle d'envoi en arrière-plan (thread séparé)."""
        last_send_time = 0.0

        while not self._stop_event.is_set():
            self._data_event.wait(timeout=0.5)
            self._data_event.clear()

            if self._stop_event.is_set():
                break

            # Récupère la donnée en attente (latest wins)
            with self._data_lock:
                data = self._pending_data
                self._pending_data = None

            if data is None:
                continue

            # Rate limiting
            now = time.time()
            elapsed = now - last_send_time
            if elapsed < self._min_send_interval:
                time.sleep(self._min_send_interval - elapsed)

            try:
                self.send(data)
            except Exception as e:
                print(f"Erreur envoi LoRa: {e}")

            last_send_time = time.time()
