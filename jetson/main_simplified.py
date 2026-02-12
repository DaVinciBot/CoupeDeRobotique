"""Main simplifié pour détection ArUco sur Jetson Nano avec caméra CSI."""

import math
import os
import time
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np
from dotenv import load_dotenv
from src.camera.csi_camera import CSICamera
from src.detector import ArucoDetector
from src.utils.timing import set_debug_mode

# Charger le fichier .env
_SCRIPT_DIR = Path(__file__).parent
load_dotenv(dotenv_path=_SCRIPT_DIR / ".env")


def parse_float_array(name: str, shape: tuple | None = None) -> np.ndarray | None:
    """Parse un tableau de floats depuis les variables d'environnement."""
    v = os.getenv(name)
    if not v:
        return None
    try:
        arr = np.array([float(x) for x in v.split()], dtype=np.float64)
        return arr.reshape(shape) if shape else arr
    except Exception:
        return None


def parse_int(name: str, default: int = 0) -> int:
    """Parse un entier depuis les variables d'environnement."""
    try:
        return int(os.getenv(name, default))
    except Exception:
        return default


def parse_float(name: str, default: float = 0.0) -> float:
    """Parse un float depuis les variables d'environnement."""
    try:
        return float(os.getenv(name, default))
    except Exception:
        return default


def parse_bool(name: str, default: bool = False) -> bool:
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

CAMERA_ID = parse_int("CAMERA_ID", 0)

# Paramètres de calibration
CAMERA_MATRIX = parse_float_array("CAMERA_MATRIX", shape=(3, 3))
DIST_COEFFS = parse_float_array("DIST_COEFFS", shape=(5,))
ASSUMED_HFOV_DEG = parse_float("ASSUMED_HFOV_DEG", 90.0)

CHESSBOARD_COLS = parse_int("CHESSBOARD_COLS", 9)
CHESSBOARD_ROWS = parse_int("CHESSBOARD_ROWS", 6)
SQUARE_SIZE_CM = parse_float("SQUARE_SIZE_CM", 2.45)
NUM_CALIB_IMAGES = parse_int("NUM_CALIB_IMAGES", 50)


def calibrate_camera() -> None:
    """Calibre la caméra avec un échiquier."""
    print("\n🎯 === MODE CALIBRATION ===\n")
    
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
    print("\n🎯 === MODE DÉTECTION ARUCO ===\n")
    
    # Vérifier que la calibration est disponible
    if CAMERA_MATRIX is None or DIST_COEFFS is None:
        print("⚠️  ATTENTION: Calibration non disponible")
        print(f"   Utilisation HFOV estimé: {ASSUMED_HFOV_DEG}°")
        print("   Pour de meilleurs résultats, lancez d'abord la calibration")
        print("   (CALIBRATE_MODE=True dans .env)\n")

    # Initialiser la caméra
    camera = CSICamera(CAMERA_ID)
    print(f"📷 Caméra: {camera.get_camera_info()}\n")

    # Initialiser le détecteur (sans tailles de marqueurs)
    detector = ArucoDetector(
        camera,
        marker_size_cm=1.0,  # Valeur factice, non utilisée
        marker_size_ref_cm=1.0,  # Valeur factice, non utilisée
        marker_size_crate_cm=1.0,  # Valeur factice, non utilisée
        camera_matrix=CAMERA_MATRIX,
        dist_coeffs=DIST_COEFFS,
        assumed_hfov_deg=ASSUMED_HFOV_DEG,
    )

    # Compteurs FPS
    frame_count = 0
    start_time = time.time()
    fps_display = 0.0

    # Créer les fenêtres
    if SHOW_CAMERA_FEED:
        cv2.namedWindow("ArUco Detection", cv2.WINDOW_NORMAL)
    if SHOW_ARENA:
        cv2.namedWindow("Arena", cv2.WINDOW_NORMAL)

    print("🚀 Détection démarrée")
    print("⌨️  'Q' ou 'ESC' pour quitter\n")

    try:
        while True:
            # Lire la frame
            frame = camera.read_frame()
            if frame is None:
                continue

            # Détection ArUco
            annotated_frame, detected_world = detector.analyze_frame(
                frame,
                show_arena=SHOW_ARENA,
                arena_window_name="Arena",
            )

            # Calcul FPS (toutes les secondes)
            frame_count += 1
            current_time = time.time()
            elapsed = current_time - start_time

            if elapsed >= 1.0:
                fps_display = frame_count / elapsed
                frame_count = 0
                start_time = current_time

                # Stats debug
                if DEBUG_MODE:
                    stats = camera.get_stats()
                    print(
                        f"📊 FPS: Traitement={fps_display:.1f} | "
                        f"Lecture={stats['read_fps']:.1f} | "
                        f"Drops={stats['frames_dropped']}"
                    )

            # Affichage feed caméra
            if SHOW_CAMERA_FEED:
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
                        f"   ID={marker_id} | "
                        f"Pos=({pos[0]:.3f}, {pos[1]:.3f})m | "
                        f"Angle={math.degrees(yaw):.1f}°"
                    )

            # Gestion des touches
            key = cv2.waitKey(1) & 0xFF
            if key == 27 or key == ord("q"):
                break

    finally:
        print("\n🛑 Arrêt de la détection")
        plt.close("all")
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    # Activer mode debug si demandé
    set_debug_mode(DEBUG_MODE)
    
    if DEBUG_MODE:
        print("🐛 Mode DEBUG activé\n")

    # Lancer calibration ou détection
    if CALIBRATE_MODE:
        calibrate_camera()
    else:
        detect_aruco()
