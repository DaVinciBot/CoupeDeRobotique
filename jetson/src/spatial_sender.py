"""Envoi du paquet spatial (header + crates) vers le robot principal via LoRa.

Format binaire identique à WinterSpatialComputation côté robot :
  Header  : 9 × int16 little-endian "<9h"
            (rx, ry, rtheta, ex, ey, etheta, evx, evy, espeed)
  Crates  : 32 × "b2hB" (zone_id: int8, x: int16, y: int16, color: uint8)

Constantes synchronisées avec CONFIG.SPATIAL_COMPUTATION_HEADER :
  xy_factor    = 10     → x/y en mètres × 10  → précision 10 cm, range ±3276 m
  angle_factor = 1000   → angle en rad × 1000 → précision 0.001 rad (~0.06°)
  format       = "<9h"  → little-endian, 9 signed int16
"""

from __future__ import annotations

import struct
from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from lora.lora import LoRa

# ── Constantes d'encodage — synchronisées avec CONFIG.SPATIAL_COMPUTATION_HEADER
# xy_factor = 10 : x/y en mètres multiplié par 10 (précision 10 cm)
XY_FACTOR: float = 10.0
# angle_factor = 1000 : angle en radians multiplié par 1000 (précision 0.001 rad)
ANGLE_FACTOR: float = 1000.0

# "<9h" : little-endian, 9 × signed int16
# Ordre : rx, ry, rtheta, ex, ey, etheta, evx, evy, espeed
HEADER_FORMAT: str = "<9h"

# Format d'une crate : int8 zone_id, int16 x, int16 y, uint8 color → "b2hB"
CRATE_FORMAT: str = "b2hB"
NUM_CRATES: int = 32

PACKET_FORMAT: str = HEADER_FORMAT + CRATE_FORMAT * NUM_CRATES
PACKET_SIZE: int = struct.calcsize(PACKET_FORMAT)


# ── Types ──────────────────────────────────────────────────────────────────────

class RobotState(NamedTuple):
    """Position + orientation d'un robot (mètres, radians)."""
    x: float
    y: float
    theta: float


class Velocity(NamedTuple):
    """Vecteur vitesse ennemi (m/s)."""
    dx: float
    dy: float
    speed: float


class CrateInfo(NamedTuple):
    """Données d'une caisse détectée."""
    zone_id: int    # -128..127  (int8)
    x: float        # mètres
    y: float        # mètres
    color: int      # 0..255  (uint8)  ex: 0=bleu, 1=jaune, 2=vide


# ── Encodage ──────────────────────────────────────────────────────────────────

def _enc_xy(v: float) -> int:
    return round(v * XY_FACTOR)


def _enc_angle(v: float) -> int:
    return round(v * ANGLE_FACTOR)


# ── Construction du paquet ────────────────────────────────────────────────────

def build_spatial_packet(
    robot: RobotState,
    enemy: RobotState,
    enemy_vel: Velocity,
    crates: list[CrateInfo],
) -> bytes:
    """Construit le paquet binaire spatial complet (header + 32 crates).

    Les crates manquantes sont remplies avec des zéros (zone_id=0, x=0,
    y=0, color=0) pour atteindre exactement NUM_CRATES entrées.

    Args:
        robot: Position/orientation du robot allié (x, y, theta).
        enemy: Position/orientation du robot ennemi (x, y, theta).
        enemy_vel: Vecteur vitesse ennemi (dx, dy, speed).
        crates: Liste de CrateInfo (au plus NUM_CRATES éléments).

    Returns:
        bytes: Paquet binaire de taille PACKET_SIZE prêt à l'envoi.

    Raises:
        ValueError: Si plus de NUM_CRATES crates sont fournies.
    """
    if len(crates) > NUM_CRATES:
        raise ValueError(
            f"Trop de crates : {len(crates)} > {NUM_CRATES}"
        )

    # Header (9 int16)
    header_fields = (
        _enc_xy(robot.x),
        _enc_xy(robot.y),
        _enc_angle(robot.theta),
        _enc_xy(enemy.x),
        _enc_xy(enemy.y),
        _enc_angle(enemy.theta),
        _enc_xy(enemy_vel.dx),
        _enc_xy(enemy_vel.dy),
        _enc_xy(enemy_vel.speed),
    )

    # Crates (padding avec des zéros si moins de NUM_CRATES)
    crate_fields: list[int] = []
    for c in crates:
        crate_fields.extend([c.zone_id, _enc_xy(c.x), _enc_xy(c.y), c.color])
    padding_count = NUM_CRATES - len(crates)
    crate_fields.extend([0] * (padding_count * 4))

    return struct.pack(PACKET_FORMAT, *header_fields, *crate_fields)


# ── Envoi via LoRa Jetson ─────────────────────────────────────────────────────

class SpatialSender:
    """Encapsule la construction + l'envoi du paquet spatial vers le robot.

    Le module LoRa Jetson (src/lora/lora.py) travaille en str UTF-8.
    On utilise un envoi direct sur le port série pour les données binaires,
    en contournant queue_send() qui ajoute un '\\n' et encode en UTF-8.
    """

    def __init__(self, lora: "LoRa") -> None:
        self._lora = lora

    def send(
        self,
        robot: RobotState,
        enemy: RobotState,
        enemy_vel: Velocity,
        crates: list[CrateInfo] | None = None,
    ) -> bool:
        """Construit et envoie le paquet spatial.

        Args:
            robot: État du robot allié.
            enemy: État du robot ennemi.
            enemy_vel: Vitesse de l'ennemi.
            crates: Liste de caisses détectées (optionnel, défaut=[]).

        Returns:
            bool: True si l'envoi a réussi, False sinon.
        """
        if crates is None:
            crates = []

        packet = build_spatial_packet(robot, enemy, enemy_vel, crates)

        if self._lora.serial is None or not self._lora.serial.is_open:
            print("❌ SpatialSender: port série LoRa non ouvert")
            return False

        try:
            # Envoi binaire direct (pas de queue_send qui ajouterait '\n')
            self._lora.serial.write(packet)
            return True
        except Exception as e:
            print(f"❌ SpatialSender: erreur envoi: {e}")
            return False


# ── Helpers : conversion depuis detected_world Jetson ────────────────────────

def crates_from_detected_world(
    detected_world: list,
    blue_id: int,
    yellow_id: int,
    empty_id: int,
) -> list[CrateInfo]:
    """Convertit detected_world (liste de (marker_id, pos, yaw)) en CrateInfo.

    Args:
        detected_world: Sortie de detector.analyze_frame() ou generate_fake_*().
        blue_id: marker_id des caisses bleues.
        yellow_id: marker_id des caisses jaunes.
        empty_id: marker_id des caisses vides.

    Returns:
        Liste de CrateInfo (au plus NUM_CRATES éléments).
    """
    color_map = {blue_id: 0, yellow_id: 1, empty_id: 2}
    result: list[CrateInfo] = []

    for marker_id, pos, _yaw in detected_world:
        if marker_id not in color_map:
            continue
        result.append(CrateInfo(
            zone_id=0,          # à remplir si vous avez l'info de zone
            x=float(pos[0]),
            y=float(pos[1]),
            color=color_map[marker_id],
        ))
        if len(result) >= NUM_CRATES:
            break

    return result