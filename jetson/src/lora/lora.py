"""Module d'envoi de données via LoRa."""

import time

import serial


class LoRa:
    """Classe d'envoi de données via LoRa."""

    def __init__(self, port: str, baudrate: int) -> None:
        """Initialise la classe LoRa.

        Args:
            port (str): Port série de la carte LoRa
            baudrate (int): Baudrate de la communication série
        """
        self.port = port
        self.baudrate = baudrate
        self.serial = None

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

    def disconnect(self) -> None:
        """Ferme la connexion série avec la carte LoRa."""
        try:
            if self.serial and self.serial.is_open:
                self.serial.close()
                print("✅ Déconnecté de la carte LoRa")
        except Exception as e:
            print(f"Erreur de déconnexion de la carte LoRa: {e}")

    def send(self, data: str) -> None:
        """Envoie des données via LoRa.

        Args:
            data (str): Données à envoyer
        """
        serial_data = data.encode("utf-8")
        if self.serial and self.serial.is_open:
            self.serial.write(serial_data)
        else:
            print(
                "Erreur: Le module LoRa n'est pas connecté.",
            )
