import os
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np

try:
    from dotenv import load_dotenv
except ImportError:

    def load_dotenv(dotenv_path: Path | None = None) -> None:
        """A minimal implementation of load_dotenv if python-dotenv is not installed."""
        p = Path(dotenv_path or ".env")
        if not p.exists():
            return
        for raw in p.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip("'\""))


from src.camera import Camera
from src.detector import ArucoDetector

load_dotenv(dotenv_path=Path(".env"))


def parse_float_array(
    name: str,
    default: np.ndarray | None = None,
    shape: tuple | None = None,
) -> np.ndarray | None:
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
    except ImportError:
        return np.array(default, dtype=np.float64).reshape(shape) if default else None


def parse_int(name: str, default: int = 0) -> int | None:
    """Parse an integer from environment variables.

    Args:
        name (str): The name of the environment variable.
        default (int, optional): The default value if the variable is not set.

    Returns:
        int | None: The parsed integer or the default value.
    """
    try:
        return int(os.getenv(name, default))
    except ImportError:
        return default


def parse_bool(name: str, default: bool = True) -> bool | None:
    """Parse a boolean from environment variables.

    Args:
        name (str): The name of the environment variable.
        default (bool, optional): The default value if the variable is not set.

    Returns:
        bool | None: The parsed boolean or the default value.
    """
    try:
        return bool(os.getenv(name, default))
    except ImportError:
        return default


SHOW_ARENA: bool | None = parse_bool("SHOW_ARENA", True)
SHOW_CAMERA_FEED: bool | None = parse_bool("SHOW_CAMERA_FEED", True)
CALIBRATE_MODE: bool | None = parse_bool("CALIBRATE_MODE", True)

CAMERA_ID: int | None = parse_int("CAMERA_ID", 0)
CAMERA_WIDTH: int | None = parse_int("CAMERA_WIDTH", 1920)
CAMERA_HEIGHT: int | None = parse_int("CAMERA_HEIGHT", 1080)

MARKER_SIZE_CM: float | None = float(os.getenv("MARKER_SIZE_CM", "2.4"))
MARKER_SIZE_REF_CM: float | None = float(os.getenv("MARKER_SIZE_REF_CM", "12.0"))
MARKER_SIZE_CRATE_CM: float | None = float(os.getenv("MARKER_SIZE_CRATE_CM", "5.0"))

ASSUMED_HFOV_DEG: float | None = float(os.getenv("ASSUMED_HFOV_DEG", "90.0"))
DIST_COEFFS: np.ndarray | None = parse_float_array("DIST_COEFFS", shape=(5,))
CAMERA_MATRIX: np.ndarray | None = parse_float_array("CAMERA_MATRIX", shape=(3, 3))
CHESSBOARD_ROWS: int | None = parse_int("CHESSBOARD_ROWS", 6)
CHESSBOARD_COLS: int | None = parse_int("CHESSBOARD_COLS", 9)
SQUARE_SIZE_CM: float | None = float(os.getenv("SQUARE_SIZE_CM", "1.0"))
NUM_CALIB_IMAGES: int | None = parse_int("NUM_CALIB_IMAGES", 20)


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
        return

    if (
        MARKER_SIZE_CM is None
        or MARKER_SIZE_REF_CM is None
        or MARKER_SIZE_CRATE_CM is None
        or SHOW_ARENA is None
        or SHOW_CAMERA_FEED is None
    ):
        print("Erreur: une ou plusieurs variables nécessaires ne sont pas définies")
        return

    camera = Camera(CAMERA_ID, width=CAMERA_WIDTH, height=CAMERA_HEIGHT)
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

    try:
        while True:
            frame = camera.read_frame()
            if frame is None:
                continue

            annotated_frame, detected_world = detector.analyze_frame(
                frame,
                show_arena=SHOW_ARENA,
                arena_window_name="Arena",
            )
            if SHOW_CAMERA_FEED:
                cv2.imshow("ArUco Detection", annotated_frame)

            for marker in detected_world:
                print(
                    f"ID Marker: {marker[0]}, Position (cm): {marker[1]}, "
                    f"Orientation (deg): {marker[2]}",
                )
            print("\n----\n")

            if cv2.waitKey(1) & 0xFF in {27, ord("q")}:
                break
    finally:
        # nettoyer les ressources matplotlib
        try:
            plt.close("all")
        except ImportError:
            print("Erreur: impossible de fermer les graphiques matplotlib.")
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    if CALIBRATE_MODE:
        calibrate_camera()
    else:
        update_in_real_time()
