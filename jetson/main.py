import math
import os
import time
from pathlib import Path
from typing import List, Optional, Tuple

import cv2
import matplotlib.pyplot as plt
import numpy as np
from dotenv import load_dotenv
from src.camera import Camera, ThreadedCamera
from src.detector import ArucoDetector
from src.utils.timing import set_debug_mode

# Charger le fichier .env depuis le même répertoire que ce script
_SCRIPT_DIR = Path(__file__).parent
load_dotenv(dotenv_path=_SCRIPT_DIR / ".env")


def detect_gpu():
    try:
        if not hasattr(cv2, "cuda"):
            return False

        count = cv2.cuda.getCudaEnabledDeviceCount()
        return count > 0
    except Exception:
        return False


def parse_float_array(
    name: str,
    default: Optional[np.ndarray] = None,
    shape: Optional[Tuple] = None,
) -> Optional[np.ndarray]:
    """Parse a float array from environment variables.

    Args:
        name (str): The name of the environment variable.
        default (np.ndarray, optional): The default value if the variable is not set.
        shape (tuple, optional): The shape to reshape the array to. Defaults to None.

    Returns:
        np.ndarray | None: The parsed float array or the default value.
    """
    v = os.getenv(name)
    if not v:
        return np.array(default, dtype=np.float64).reshape(shape) if default else None
    try:
        arr = np.array([float(x) for x in v.split()], dtype=np.float64)
        return arr.reshape(shape) if shape else arr
    except Exception:
        return np.array(default, dtype=np.float64).reshape(shape) if default else None


def parse_int(name: str, default: int = 0) -> Optional[int]:
    """Parse an integer from environment variables.

    Args:
        name (str): The name of the environment variable.
        default (int, optional): The default value if the variable is not set.

    Returns:
        int | None: The parsed integer or the default value.
    """
    try:
        return int(os.getenv(name, default))
    except Exception:
        return default


def parse_bool(name: str, default: bool = True) -> bool:
    """Parse a boolean from environment variables.

    Args:
        name (str): The name of the environment variable.
        default (bool, optional): The default value if the variable is not set.

    Returns:
        bool: The parsed boolean or the default value.
    """
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"true", "1", "yes", "on"}


SHOW_ARENA: bool = parse_bool("SHOW_ARENA", default=True)
SHOW_CAMERA_FEED: bool = parse_bool("SHOW_CAMERA_FEED", default=True)
CALIBRATE_MODE: bool = parse_bool("CALIBRATE_MODE", default=False)
DEBUG_MODE: bool = parse_bool("DEBUG_MODE", default=False)
USE_THREADED_CAMERA: bool = parse_bool("USE_THREADED_CAMERA", default=True)

CAMERA_ID: Optional[int] = parse_int("CAMERA_ID", 0)

# Configuration FPS
FPS: int = parse_int("FPS", 15)  # FPS de la caméra

CAMERA_WIDTH: Optional[int] = parse_int("CAMERA_WIDTH", 1920)
CAMERA_HEIGHT: Optional[int] = parse_int("CAMERA_HEIGHT", 1080)

# Backend OpenCV (optionnel)
CAMERA_BACKEND_STR: Optional[str] = os.getenv("CAMERA_BACKEND", "").strip().upper()
CAMERA_BACKEND: Optional[List[int]] = None
if CAMERA_BACKEND_STR:
    backend_map = {
        "V4L2": cv2.CAP_V4L2 if hasattr(cv2, "CAP_V4L2") else None,
        "DSHOW": cv2.CAP_DSHOW if hasattr(cv2, "CAP_DSHOW") else None,
        "MSMF": cv2.CAP_MSMF if hasattr(cv2, "CAP_MSMF") else None,
        "ANY": cv2.CAP_ANY,
    }
    backend_id = backend_map.get(CAMERA_BACKEND_STR)
    if backend_id is not None:
        CAMERA_BACKEND = [backend_id]
        print(f"🔧 Backend forcé: {CAMERA_BACKEND_STR}")
    else:
        print(f"⚠️  Backend inconnu: {CAMERA_BACKEND_STR}, utilisation auto")

MARKER_SIZE_CM: Optional[float] = float(os.getenv("MARKER_SIZE_CM", "2.4"))
MARKER_SIZE_REF_CM: Optional[float] = float(os.getenv("MARKER_SIZE_REF_CM", "12.0"))
MARKER_SIZE_CRATE_CM: Optional[float] = float(os.getenv("MARKER_SIZE_CRATE_CM", "5.0"))

ASSUMED_HFOV_DEG: Optional[float] = float(os.getenv("ASSUMED_HFOV_DEG", "90.0"))
DIST_COEFFS: Optional[np.ndarray] = parse_float_array("DIST_COEFFS", shape=(5,))
CAMERA_MATRIX: Optional[np.ndarray] = parse_float_array("CAMERA_MATRIX", shape=(3, 3))
CHESSBOARD_ROWS: Optional[int] = parse_int("CHESSBOARD_ROWS", 6)
CHESSBOARD_COLS: Optional[int] = parse_int("CHESSBOARD_COLS", 9)
SQUARE_SIZE_CM: Optional[float] = float(os.getenv("SQUARE_SIZE_CM", "1.0"))
NUM_CALIB_IMAGES: Optional[int] = parse_int("NUM_CALIB_IMAGES", 20)


def calibrate_camera() -> None:
    """Calibrate the camera using chessboard images."""
    if (
        CAMERA_ID is None
        or CHESSBOARD_COLS is None
        or CHESSBOARD_ROWS is None
        or SQUARE_SIZE_CM is None
        or NUM_CALIB_IMAGES is None
    ):
        print("Erreur: une ou plusieurs variables nécessaires ne sont pas définies")
        return
    camera = Camera(
        CAMERA_ID,
        width=CAMERA_WIDTH,
        height=CAMERA_HEIGHT,
        backends=CAMERA_BACKEND,
        use_mjpg=False,
        fps=5,
    )
    if not camera.is_opened():
        print("Erreur: impossible d'ouvrir la caméra")
        return

    camera_matrix, dist_coeffs, _, _ = camera.calibrate(
        chessboard_size=(CHESSBOARD_COLS, CHESSBOARD_ROWS),
        square_size=SQUARE_SIZE_CM,
        num_images=NUM_CALIB_IMAGES,
    )

    camera.release()

    if camera_matrix is not None and dist_coeffs is not None:
        print("Calibration réussie")
        print(f'CAMERA_MATRIX="{" ".join(map(str, camera_matrix.ravel()))}"')
        print(f'DIST_COEFFS="{" ".join(map(str, dist_coeffs.ravel()))}"')
    else:
        print("Échec de la calibration")


def update_in_real_time() -> None:
    """Update ArUco marker detection in real-time."""
    if (
        CAMERA_ID is None
        or CAMERA_MATRIX is None
        or DIST_COEFFS is None
        or ASSUMED_HFOV_DEG is None
    ):
        print("Erreur: une ou plusieurs variables nécessaires ne sont pas définies")
        print(
            str(CAMERA_ID)
            + " "
            + str(CAMERA_MATRIX)
            + " "
            + str(DIST_COEFFS)
            + " "
            + str(ASSUMED_HFOV_DEG)
        )
        return

    if (
        MARKER_SIZE_CM is None
        or MARKER_SIZE_REF_CM is None
        or MARKER_SIZE_CRATE_CM is None
    ):
        print("Erreur: une ou plusieurs variables nécessaires ne sont pas définies")
        return

    # Utiliser ThreadedCamera si activé, sinon Camera standard
    print(f"🎥 Démarrage caméra avec FPS={FPS}")

    if USE_THREADED_CAMERA:
        print("🚀 Mode THREADED activé")
        camera = ThreadedCamera(
            CAMERA_ID,
            width=CAMERA_WIDTH,
            height=CAMERA_HEIGHT,
            backends=CAMERA_BACKEND,
            fps=FPS,
        )
    else:
        camera = Camera(
            CAMERA_ID,
            width=CAMERA_WIDTH,
            height=CAMERA_HEIGHT,
            backends=CAMERA_BACKEND,
            fps=FPS,
        )

    if not camera.is_opened():
        print("Erreur: impossible d'ouvrir la caméra")
        return

    detector = ArucoDetector(
        camera,
        marker_size_cm=MARKER_SIZE_CM,
        marker_size_ref_cm=MARKER_SIZE_REF_CM,
        marker_size_crate_cm=MARKER_SIZE_CRATE_CM,
        camera_matrix=CAMERA_MATRIX,
        dist_coeffs=DIST_COEFFS,
        assumed_hfov_deg=ASSUMED_HFOV_DEG,
    )

    print(f"🎥 Caméra: {camera.get_camera_info()}")
    # Compteurs pour FPS
    frame_count = 0
    start_time = time.time()
    fps_display = 0.0

    # Pré-calculer les constantes pour éviter les lookups répétés
    show_feed = SHOW_CAMERA_FEED
    show_arena = SHOW_ARENA
    debug_mode = DEBUG_MODE
    use_threaded = USE_THREADED_CAMERA

    if show_feed:
        cv2.namedWindow("ArUco Detection", cv2.WINDOW_NORMAL)
    if show_arena:
        cv2.namedWindow("Arena", cv2.WINDOW_NORMAL)

    try:
        while True:
            # Lecture de frame (opération la plus critique)
            frame = camera.read_frame()
            if frame is None:
                continue

            # Détection et analyse (CPU intensif)
            annotated_frame, detected_world = detector.analyze_frame(
                frame,
                show_arena=show_arena,
                arena_window_name="Arena",
            )

            # Calcul FPS (seulement toutes les secondes)
            frame_count += 1
            current_time = time.time()
            elapsed = current_time - start_time

            if elapsed >= 1.0:
                fps_display = frame_count / elapsed
                frame_count = 0
                start_time = current_time

                # Debug stats (seulement si DEBUG_MODE activé)
                if debug_mode and use_threaded and hasattr(camera, "get_stats"):
                    stats = camera.get_stats()
                    print(
                        f"📊 FPS | Traitement: {fps_display:.1f} | "
                        f"Lecture: {stats['read_fps']:.1f} | "
                        f"Drops: {stats['frames_dropped']}"
                    )

            # Affichage image (optimisé - une seule condition)
            if show_feed:
                # Texte FPS pré-formaté
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

            # Affichage markers (seulement si DEBUG et des markers détectés)
            if debug_mode and detected_world:
                for marker in detected_world:
                    print(
                        f"ID: {marker[0]}, "
                        f"Pos(m): ({marker[1][0]:.3f}, {marker[1][1]:.3f}), "
                        f"Angle: {math.degrees(marker[2]):.1f}°"
                    )

            # Vérifier sortie (Q ou ESC) - optimisé
            key = cv2.waitKey(1) & 0xFF
            if key == 27 or key == ord("q"):
                break
    finally:
        # nettoyer les ressources matplotlib
        try:
            plt.close("all")
        except Exception:
            print("Erreur: impossible de fermer les graphiques matplotlib.")
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    USE_GPU = detect_gpu()
    if USE_GPU:
        print("⚡️ Using CUDA acceleration")

    # Activer le mode debug si demandé
    set_debug_mode(DEBUG_MODE)
    if DEBUG_MODE:
        print("🐛 Mode DEBUG activé")

    if CALIBRATE_MODE:
        calibrate_camera()
    else:
        update_in_real_time()
