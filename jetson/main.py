import math
import os
import time
from pathlib import Path
from typing import Optional, Tuple

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
FPS: Optional[int] = parse_int("FPS", 15)
CAMERA_WIDTH: Optional[int] = parse_int("CAMERA_WIDTH", 1920)
CAMERA_HEIGHT: Optional[int] = parse_int("CAMERA_HEIGHT", 1080)

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
    camera = Camera(CAMERA_ID, width=CAMERA_WIDTH, height=CAMERA_HEIGHT)
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
    if USE_THREADED_CAMERA:
        print("🚀 Mode THREADED activé pour améliorer les performances")
        camera = ThreadedCamera(
            CAMERA_ID, width=CAMERA_WIDTH, height=CAMERA_HEIGHT, fps=FPS
        )
    else:
        camera = Camera(CAMERA_ID, width=CAMERA_WIDTH, height=CAMERA_HEIGHT, fps=FPS)

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

    print(f"Caméra: {camera.get_camera_info()}")
    cv2.namedWindow("ArUco Detection", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Arena", cv2.WINDOW_NORMAL)

    # Compteurs pour FPS
    frame_count = 0
    start_time = time.time()
    fps_display = 0.0

    try:
        while True:
            loop_start = time.time()

            frame = camera.read_frame()
            if frame is None:
                continue

            annotated_frame, detected_world = detector.analyze_frame(
                frame,
                show_arena=SHOW_ARENA,
                arena_window_name="Arena",
            )

            # Calculer et afficher FPS
            frame_count += 1
            elapsed = time.time() - start_time
            if elapsed >= 1.0:
                fps_display = frame_count / elapsed
                frame_count = 0
                start_time = time.time()

                # Afficher stats si threaded camera
                if USE_THREADED_CAMERA and hasattr(camera, "get_stats"):
                    stats = camera.get_stats()
                    print(
                        f"📊 FPS traitement: {fps_display:.1f} | FPS lecture caméra: {stats['read_fps']:.1f} | Frames droppées: {stats['frames_dropped']}"
                    )
                else:
                    print(f"📊 FPS: {fps_display:.1f}")

            # Afficher FPS sur l'image
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

            # Affichage des marqueurs détectés (moins verbose)
            if DEBUG_MODE and len(detected_world) > 0:
                for marker in detected_world:
                    print(
                        f"ID: {marker[0]}, Pos(m): ({marker[1][0]:.3f}, {marker[1][1]:.3f}), "
                        f"Angle: {math.degrees(marker[2]):.1f}°",
                    )

            if cv2.waitKey(1) & 0xFF in {27, ord("q")}:
                break

            # Afficher temps de boucle en mode debug
            if DEBUG_MODE:
                loop_time = (time.time() - loop_start) * 1000
                print(f"⏱️  Temps boucle totale: {loop_time:.2f} ms")
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
    print("USE_GPU =", USE_GPU)

    # Activer le mode debug si demandé
    set_debug_mode(DEBUG_MODE)
    if DEBUG_MODE:
        print("🐛 Mode DEBUG activé - Chronométrage des fonctions")

    if CALIBRATE_MODE:
        calibrate_camera()
    else:
        update_in_real_time()
