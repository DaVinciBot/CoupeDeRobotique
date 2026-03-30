"""Main pour détection ArUco sur Jetson Nano avec caméra CSI."""

import math
import os
import time
from pathlib import Path
from typing import Optional

import cv2
import matplotlib.pyplot as plt
import numpy as np
from dotenv import load_dotenv
from src.camera import CSICamera
from src.detector import ArucoDetector
from src.lora.lora import LoRa
from src.utils.timing import set_debug_mode

# Charger le fichier .env
_SCRIPT_DIR = Path(__file__).parent
load_dotenv(dotenv_path=_SCRIPT_DIR / ".env")


def parse_float_array(name, shape=None):
    # type: (str, Optional[tuple]) -> Optional[np.ndarray]
    """Parse un tableau de floats depuis les variables d'environnement."""
    v = os.getenv(name)
    if not v:
        return None
    try:
        arr = np.array([float(x) for x in v.split()], dtype=np.float64)
        return arr.reshape(shape) if shape else arr
    except Exception:
        return None


def parse_int_array(name, shape=None):
    # type: (str, Optional[tuple]) -> Optional[np.ndarray]
    """Parse un tableau d'entiers depuis les variables d'environnement."""
    v = os.getenv(name)
    if not v:
        return None
    try:
        arr = np.array([int(x) for x in v.split()], dtype=np.int32)
        return arr.reshape(shape) if shape else arr
    except Exception:
        return None


def parse_int(name, default=0):
    # type: (str, int) -> int
    """Parse un entier depuis les variables d'environnement."""
    try:
        return int(os.getenv(name, default))
    except Exception:
        return default


def parse_float(name, default=0.0):
    # type: (str, float) -> float
    """Parse un float depuis les variables d'environnement."""
    try:
        return float(os.getenv(name, default))
    except Exception:
        return default


def parse_bool(name, default=False):
    # type: (str, bool) -> bool
    """Parse un booléen depuis les variables d'environnement."""
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"true", "1", "yes", "on"}


# === Configuration ===
CALIBRATE_MODE = parse_bool("CALIBRATE_MODE", False)
DEBUG_MODE = parse_bool("DEBUG_MODE", False)
SHOW_ARENA = parse_bool("SHOW_ARENA", True)
SHOW_CAMERA_FEED = parse_bool("SHOW_CAMERA_FEED", True)

HAS_DISPLAY = bool(
    os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"),
)

DUMMY_LORA = parse_bool("DUMMY_LORA", False)
DUMMY_DETECTION = parse_bool("DUMMY_DETECTION", False)

CAMERA_ID = parse_int("CAMERA_ID", 0)

# Paramètres de calibration
CAMERA_MATRIX = parse_float_array("CAMERA_MATRIX", shape=(3, 3))
DIST_COEFFS = parse_float_array("DIST_COEFFS", shape=(5,))
ASSUMED_HFOV_DEG = parse_float("ASSUMED_HFOV_DEG", 90.0)

CHESSBOARD_COLS = parse_int("CHESSBOARD_COLS", 9)
CHESSBOARD_ROWS = parse_int("CHESSBOARD_ROWS", 6)
SQUARE_SIZE_CM = parse_float("SQUARE_SIZE_CM", 2.45)
NUM_CALIB_IMAGES = parse_int("NUM_CALIB_IMAGES", 50)

ROBOT_MARKER_ID = parse_int("ROBOT_MARKER_ID", 6)
ENEMY_MARKER_ID = parse_int("ENEMY_MARKER_ID", 1)
REFERENCES_MARKER_IDS = parse_int_array("REFERENCES_MARKER_IDS")
BLUE_CRATE_MARKER_ID = parse_int("BLUE_CRATE_MARKER_ID", 36)
YELLOW_CRATE_MARKER_ID = parse_int("YELLOW_CRATE_MARKER_ID", 47)
EMPTY_CRATE_MARKER_ID = parse_int("EMPTY_CRATE_MARKER_ID", 41)


def generate_fake_detected_world():
    """Génère des données de détection fictives pour le mode DUMMY_DETECTION."""
    fake_data = [
        # === 4 marqueurs de référence ===
        (20, np.array([0.600, 1.400]), math.pi / 2),
        (21, np.array([2.400, 1.400]), math.pi / 2),
        (22, np.array([0.600, 0.600]), math.pi / 2),
        (23, np.array([2.400, 0.600]), math.pi / 2),
        # === Robot principal bleu (ID 1) ===
        (1, np.array([0.800, 1.000]), math.pi),
        # === Robot principal jaune (ID 6) ===
        (6, np.array([2.200, 1.000]), 0.0),
        # === Caisses dans les zones de ramassage ===
        # Zone de ramassage
        (36, np.array([0.175, 0.725]), 0.0),
        (47, np.array([0.175, 0.775]), 0.0),
        (36, np.array([0.175, 0.825]), 0.0),
        (47, np.array([0.175, 0.875]), 0.0),
        # Zone de ramassage
        (36, np.array([0.175, 1.525]), 0.0),
        (47, np.array([0.175, 1.575]), 0.0),
        (36, np.array([0.175, 1.625]), 0.0),
        (47, np.array([0.175, 1.675]), 0.0),
        # Zone de ramassage
        (36, np.array([1.175, 1.800]), math.pi / 2),
        (36, np.array([1.125, 1.800]), math.pi / 2),
        (47, np.array([1.075, 1.800]), math.pi / 2),
        (47, np.array([1.025, 1.800]), math.pi / 2),
        # Zone de ramassage
        (47, np.array([1.825, 1.800]), math.pi / 2),
        (36, np.array([1.875, 1.800]), math.pi / 2),
        (36, np.array([1.925, 1.800]), math.pi / 2),
        (47, np.array([1.975, 1.800]), math.pi / 2),
        # Zone de ramassage
        (47, np.array([1.225, 1.200]), math.pi / 2),
        (36, np.array([1.175, 1.200]), math.pi / 2),
        (36, np.array([1.125, 1.200]), math.pi / 2),
        (47, np.array([1.075, 1.200]), math.pi / 2),
        # Zone de ramassage
        (47, np.array([1.775, 1.200]), math.pi / 2),
        (47, np.array([1.825, 1.200]), math.pi / 2),
        (36, np.array([1.875, 1.200]), math.pi / 2),
        (36, np.array([1.925, 1.200]), math.pi / 2),
        # Zone de ramassage
        (36, np.array([2.825, 0.725]), 0.0),
        (47, np.array([2.825, 0.775]), 0.0),
        (36, np.array([2.825, 0.825]), 0.0),
        (47, np.array([2.825, 0.875]), 0.0),
        # Zone de ramassage
        (36, np.array([2.825, 1.525]), 0.0),
        (47, np.array([2.825, 1.575]), 0.0),
        (36, np.array([2.825, 1.625]), 0.0),
        (47, np.array([2.825, 1.675]), 0.0),
        # === Caisses vides dans les zones de chargement ===
        # Zone de chargement
        (41, np.array([2.250, 0.325]), math.pi / 2),
        (41, np.array([2.200, 0.325]), math.pi / 2),
        (41, np.array([2.150, 0.325]), math.pi / 2),
        # Zone de chargement
        (41, np.array([0.750, 0.325]), math.pi / 2),
        (41, np.array([0.800, 0.325]), math.pi / 2),
        (41, np.array([0.850, 0.325]), math.pi / 2),
        # Zone de frigo
        (47, np.array([1.075, 0.275]), math.pi / 2),
        (36, np.array([1.125, 0.275]), math.pi / 2),
        # Zone de frigo
        (47, np.array([1.925, 0.275]), math.pi / 2),
        (36, np.array([1.875, 0.275]), math.pi / 2),
        # Zone de frigo
        (47, np.array([1.325, 0.225]), math.pi / 2),
        (36, np.array([1.375, 0.225]), math.pi / 2),
        # Zone de frigo
        (47, np.array([1.625, 0.225]), math.pi / 2),
        (36, np.array([1.675, 0.225]), math.pi / 2),
    ]
    # === 6 PAMIs bleus (IDs 51-56) — dans le nid bleu ===
    for i, pami_id in enumerate(range(51, 57)):
        fake_data.append((
            pami_id,
            np.array([0.100 + i % 3 * 0.11, 0.050 + i % 2 * 0.11]),
            math.pi / 2,
        ))
    # === 6 PAMIs jaunes (IDs 71-76) — dans le nid jaune ===
    for i, pami_id in enumerate(range(71, 77)):
        fake_data.append((
            pami_id,
            np.array([2.900 - i % 3 * 0.11, 0.050 + i % 2 * 0.11]),
            math.pi / 2,
        ))
    return fake_data


def calibrate_camera() -> None:
    """Calibre la caméra avec un échiquier."""
    print("\n=== MODE CALIBRATION ===\n")

    camera = CSICamera(CAMERA_ID)

    camera_matrix, dist_coeffs, _, _ = camera.calibrate(
        chessboard_size=(CHESSBOARD_COLS, CHESSBOARD_ROWS),
        square_size=SQUARE_SIZE_CM,
        num_images=NUM_CALIB_IMAGES,
    )

    camera.release()

    if camera_matrix is not None and dist_coeffs is not None:
        print("\n✅ === CALIBRATION RÉUSSIE ===\n")
        print("Copiez ces lignes dans votre fichier .env:\n")
        print(f'CAMERA_MATRIX="{" ".join(map(str, camera_matrix.ravel()))}"')
        print(f'DIST_COEFFS="{" ".join(map(str, dist_coeffs.ravel()))}"')
        print()
    else:
        print("\n❌ Échec de la calibration\n")


def detect_aruco() -> None:
    """Détection ArUco en temps réel."""
    print("\n=== MODE DÉTECTION ===\n")

    # Initialiser la caméra et le détecteur
    camera = None
    detector = None
    if not DUMMY_DETECTION:
        print("📷 Initialisation de la caméra...")
        camera = CSICamera(CAMERA_ID)
        print("🔍 Initialisation du détecteur ArUco...")
        detector = ArucoDetector(
            camera,
            camera_matrix=CAMERA_MATRIX,
            dist_coeffs=DIST_COEFFS,
            assumed_hfov_deg=ASSUMED_HFOV_DEG,
        )
    else:
        print("📷 Caméra/Détection désactivés (DUMMY_DETECTION=True)")

    # Détecteur minimal pour l'affichage arena en mode dummy
    arena_detector = None
    if DUMMY_DETECTION and SHOW_ARENA:
        arena_detector = ArucoDetector(
            None,
            camera_matrix=CAMERA_MATRIX,
            dist_coeffs=DIST_COEFFS,
        )

    # Initialiser LoRa
    lora = None
    if not DUMMY_LORA:
        print("📡 Initialisation de la carte LoRa...")
        lora = LoRa(
            port="/dev/ttyTHS1",
            baudrate=115200,
        )
        lora.connect()
        lora.start()
    else:
        print("📡 LoRa désactivé (DUMMY_LORA=True)")

    # Compteurs FPS
    frame_count = 0
    start_time = time.time()
    fps_display = 0.0

    # Créer les fenêtres
    if HAS_DISPLAY and SHOW_CAMERA_FEED and not DUMMY_DETECTION:
        cv2.namedWindow("ArUco Detection", cv2.WINDOW_NORMAL)
    if HAS_DISPLAY and SHOW_ARENA:
        cv2.namedWindow("Arena", cv2.WINDOW_NORMAL)

    print("🚀 Démarrage de la détection...")

    try:
        while True:
            if not DUMMY_DETECTION:
                # Lire la frame
                frame = camera.read_frame(copy=SHOW_CAMERA_FEED)
                if frame is None:
                    continue

                # Détection ArUco
                annotated_frame, detected_world = detector.analyze_frame(
                    frame,
                    show_arena=SHOW_ARENA,
                    arena_window_name="Arena",
                    show_video=SHOW_CAMERA_FEED,
                )
            else:
                # Données fictives
                detected_world = generate_fake_detected_world()
                annotated_frame = None
                # Affichage arena avec les faux marqueurs
                if SHOW_ARENA and arena_detector is not None:
                    arena_detector.update_arena_display(
                        detected_world=detected_world,
                        window_name="Arena",
                    )
                time.sleep(1.0 / 15)  # Simuler ~15 FPS

            # Calcul FPS (toutes les secondes)
            frame_count += 1
            current_time = time.time()
            elapsed = current_time - start_time

            if elapsed >= 1.0:
                fps_display = frame_count / elapsed
                frame_count = 0
                start_time = current_time

                # Stats debug (caméra réelle uniquement)
                if DEBUG_MODE and camera is not None:
                    stats = camera.get_stats()
                    print(
                        f"📊 FPS: Traitement={fps_display:.1f} | "
                        f"Lecture={stats['read_fps']:.1f} | "
                        f"Drops={stats['frames_dropped']}"
                    )

            # Affichage feed caméra (détection réelle uniquement)
            if HAS_DISPLAY and SHOW_CAMERA_FEED and annotated_frame is not None:
                cv2.putText(
                    annotated_frame,
                    f"FPS: {fps_display:.1f}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    (0, 255, 0),
                    2,
                )
                cv2.imshow("ArUco Detection", annotated_frame)

            # Affichage markers debug
            if DEBUG_MODE and detected_world:
                for marker_id, pos, yaw in detected_world:
                    print(
                        f"   ID={marker_id} | ",
                        f"Pos=({pos[0]:.3f}, {pos[1]:.3f})m | ",
                        f"Angle={math.degrees(yaw):.1f}°",
                    )

            # Determiner la vitesse des robots

            # Formattage du message LoRa
            t = time.localtime()
            msg = f"CD_{t.tm_hour}:{t.tm_min}:{t.tm_sec}[\r\n"
            for marker_id, pos, yaw in detected_world:
                deg = math.degrees(yaw)
                msg += f'"{marker_id}|{pos[0]:.3f}|{pos[1]:.3f}|{deg:.1f}",\r\n'
            msg += "]\r\n"

            # Envoi via LoRa ou affichage debug
            if lora is not None:
                lora.queue_send(msg)
            elif DEBUG_MODE:
                print(f"📡 [DUMMY_LORA] {msg.strip()}")

            # Gestion des touches (uniquement si fenêtres OpenCV ouvertes)
            if HAS_DISPLAY and (
                (SHOW_CAMERA_FEED and not DUMMY_DETECTION) or SHOW_ARENA
            ):
                key = cv2.waitKey(1) & 0xFF
                if key == 27 or key == ord("q"):
                    break

    finally:
        print("\n🛑 Arrêt de la détection")
        plt.close("all")
        if camera is not None:
            camera.release()
        if HAS_DISPLAY:
            cv2.destroyAllWindows()
        if lora is not None:
            lora.stop()
            lora.disconnect()


if __name__ == "__main__":
    # Activer mode debug si demandé
    set_debug_mode(DEBUG_MODE)

    if DEBUG_MODE:
        print("🐛 Démarrage en mode DEBUG")

    # Lancer calibration ou détection
    if CALIBRATE_MODE:
        calibrate_camera()
    else:
        detect_aruco()
