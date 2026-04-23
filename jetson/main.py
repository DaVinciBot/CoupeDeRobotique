"""Main pour détection ArUco sur Jetson Nano avec caméra CSI."""

import os

# Doit être défini AVANT import cv2 pour supprimer le warning
# "Cannot query video position" sur flux caméra live GStreamer.
os.environ.setdefault("OPENCV_LOG_LEVEL", "ERROR")
os.environ.setdefault("GST_DEBUG", "0")

import contextlib
import math
import select
import sys
import termios
import threading
import time
import tty
from collections import deque
from pathlib import Path
from typing import Optional

import cv2

with contextlib.suppress(AttributeError):
    cv2.utils.logging.setLogLevel(cv2.utils.logging.LOG_LEVEL_ERROR)
import matplotlib.pyplot as plt
import numpy as np
from dotenv import load_dotenv
from src.arena import arena_elements
from src.camera import CSICamera
from src.detector import ArucoDetector
from src.game import MatchState
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

# Résolution pour le writer GStreamer (doit correspondre à la caméra)
GST_DISPLAY_WIDTH = 1920
GST_DISPLAY_HEIGHT = 1080
GST_DISPLAY_FPS = 15

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
ZONE_TOLERANCE_M = parse_float("ZONE_TOLERANCE_CM", 5.0) / 100.0
SPEED_HISTORY_SIZE = 15  # ~1 seconde à 15 FPS


# === Zones combinées pour la recherche ===
_ALL_ZONES = arena_elements["zone_depot"] + arena_elements["zone_ramassage"]


def compute_speed(history):
    """Calcule la vitesse en m/s depuis un historique de positions (deque)."""
    if len(history) < 2:
        return 0.0
    t_old, x_old, y_old = history[0]
    t_new, x_new, y_new = history[-1]
    dt = t_new - t_old
    if dt < 0.01:
        return 0.0
    dist = math.sqrt((x_new - x_old) ** 2 + (y_new - y_old) ** 2)
    return dist / dt


def find_zone_for_kapla(x, y, tolerance):
    """Retourne l'id_zone si (x, y) est dans une zone (avec tolérance), sinon -1."""
    for zone in _ALL_ZONES:
        zx, zy = zone["position"]
        if (zx - tolerance <= x <= zx + zone["width"] + tolerance
                and zy - tolerance <= y <= zy + zone["height"] + tolerance):
            return zone["id_zone"]
    return -1


def group_kapla_by_zone(detected_world, tolerance):
    """Groupe les kapla par zone et couleur.

    Returns:
        zoned: dict {zone_id: {"B": [(x,y,deg), ...], "Y": [...]}}
        unzoned: list [(x, y, deg), ...]
    """
    zoned = {}
    unzoned = []

    for marker_id, pos, yaw in detected_world:
        if marker_id == BLUE_CRATE_MARKER_ID:
            color = "B"
        elif marker_id == YELLOW_CRATE_MARKER_ID:
            color = "Y"
        else:
            continue

        x, y = float(pos[0]), float(pos[1])
        deg = math.degrees(yaw)
        zone_id = find_zone_for_kapla(x, y, tolerance)

        if zone_id == -1:
            unzoned.append((x, y, deg))
        else:
            if zone_id not in zoned:
                zoned[zone_id] = {"B": [], "Y": []}
            zoned[zone_id][color].append((x, y, deg))

    return zoned, unzoned


def build_lora_message(detected_world, robot_speeds, tolerance):
    """Construit le message vision (cmd 5) sur une seule ligne.

    Format: `5|R|id|x|y|deg|speed|...|Z|zone|c|x|y|deg|...|U|x|y|deg|...\\n`
    Les tokens R/Z/U délimitent les enregistrements côté récepteur.
    """
    parts = ["5"]

    # Robots
    for marker_id, pos, yaw in detected_world:
        if marker_id in (ROBOT_MARKER_ID, ENEMY_MARKER_ID):
            speed = robot_speeds.get(marker_id, 0.0)
            deg = math.degrees(yaw)
            parts.extend([
                "R",
                str(marker_id),
                f"{pos[0]:.3f}",
                f"{pos[1]:.3f}",
                f"{deg:.1f}",
                f"{speed:.2f}",
            ])

    # Kapla groupés par zone
    zoned, unzoned = group_kapla_by_zone(detected_world, tolerance)
    for zone_id in sorted(zoned.keys()):
        for color in ("B", "Y"):
            for x, y, deg in zoned[zone_id][color]:
                parts.extend([
                    "Z",
                    str(zone_id),
                    color,
                    f"{x:.3f}",
                    f"{y:.3f}",
                    f"{deg:.1f}",
                ])
    for x, y, deg in unzoned:
        parts.extend(["U", f"{x:.3f}", f"{y:.3f}", f"{deg:.1f}"])

    return "|".join(parts) + "\n"


def generate_fake_detected_world():
    """Génère des données de détection fictives pour le mode DUMMY_DETECTION.

    Les robots font un aller-retour de 1m en boucle de 4 secondes:
    0-2s: avance de 1m, 2-4s: demi-tour + avance de 1m (retour).
    """
    # Cycle de 4 secondes pour le mouvement des robots
    cycle = time.time() % 4.0
    if cycle < 2.0:
        progress = cycle / 2.0  # 0 -> 1
        robot1_angle = 0.0       # face droite
        robot6_angle = math.pi   # face gauche
    else:
        progress = (cycle - 2.0) / 2.0  # 0 -> 1
        robot1_angle = math.pi   # demi-tour
        robot6_angle = 0.0       # demi-tour

    # Robot bleu (ID 1): aller-retour sur X entre 0.8 et 1.8
    if cycle < 2.0:
        r1_x = 0.800 + progress * 1.0
    else:
        r1_x = 1.800 - progress * 1.0

    # Robot jaune (ID 6): aller-retour sur X entre 1.2 et 2.2
    if cycle < 2.0:
        r6_x = 2.200 - progress * 1.0
    else:
        r6_x = 1.200 + progress * 1.0

    fake_data = [
        # === 4 marqueurs de référence ===
        (20, np.array([0.600, 1.400]), math.pi / 2),
        (21, np.array([2.400, 1.400]), math.pi / 2),
        (22, np.array([0.600, 0.600]), math.pi / 2),
        (23, np.array([2.400, 0.600]), math.pi / 2),
        # === Robot principal bleu (ID 1) — mouvement dynamique ===
        (1, np.array([r1_x, 1.000]), robot1_angle),
        # === Robot principal jaune (ID 6) — mouvement dynamique ===
        (6, np.array([r6_x, 1.000]), robot6_angle),
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


def start_keyboard_thread(lora, match_state, get_detected_world, get_robot_speeds):
    """Lance un thread clavier pour envoyer des commandes LoRa.

    Touches : 2=ID PAMI, 3=dépôts, 5=vision.
    1 et 4 sont reçues uniquement.
    """
    stop = threading.Event()

    def _read_keys():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)
            while not stop.is_set():
                if select.select([sys.stdin], [], [], 0.2)[0]:
                    ch = sys.stdin.read(1)
                    if ch == "2":
                        pid = match_state.register_pami()
                        msg = f"2|{pid}\n"
                        lora.queue_send(msg)
                        print(f"⌨️  [2] ID PAMI attribué: {pid}  →  {msg.strip()}")
                    elif ch == "3":
                        if match_state.team_color is None:
                            print(
                                "⌨️  [3] Pas de couleur définie. "
                                "Appuie sur B (bleu) ou Y (jaune) :",
                            )
                            while not stop.is_set():
                                if select.select([sys.stdin], [], [], 0.5)[0]:
                                    col = sys.stdin.read(1).upper()
                                    if col in ("B", "Y"):
                                        match_state.start_match(col)
                                        print(f"⌨️  Couleur forcée: {col}")
                                        break
                                    print("⌨️  Touche invalide, B ou Y attendu")
                        assignments = match_state.compute_depot_assignments(
                            arena_elements,
                        )
                        msg = MatchState.build_msg_3(assignments)
                        lora.queue_send(msg)
                        print(
                            f"⌨️  [3] Dépôts envoyés ({len(assignments)} PAMI)  →  "
                            f"{msg.strip()}"
                        )
                    elif ch == "5":
                        detected = get_detected_world()
                        speeds = get_robot_speeds()
                        msg = build_lora_message(
                            detected,
                            speeds,
                            ZONE_TOLERANCE_M,
                        )
                        lora.queue_send(msg)
                        print(f"⌨️  [5] Vision envoyée  →  {msg.strip()[:80]}...")
                    elif ch == "1":
                        print("⌨️  [1] Commande reçue uniquement (demande ID PAMI)")
                    elif ch == "4":
                        print("⌨️  [4] Commande reçue uniquement (démarrage match)")
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    t = threading.Thread(target=_read_keys, daemon=True)
    t.start()
    return stop


CALIBRATION_FILE = os.getenv("CALIBRATION_FILE", "calibration.npz")


def load_calibration_file():
    """Charge la calibration depuis un fichier .npz si disponible."""
    path = _SCRIPT_DIR / CALIBRATION_FILE
    if path.exists():
        data = np.load(str(path))
        cam_mtx = data["camera_matrix"]
        dist = data["dist_coeffs"]
        print(f"📂 Calibration chargée depuis {CALIBRATION_FILE}")
        return cam_mtx, dist
    return None, None


def calibrate_camera() -> None:
    """Calibre la caméra avec un échiquier (auto-capture)."""
    print("\n=== MODE CALIBRATION ===\n")

    camera = CSICamera(CAMERA_ID)

    save_path = str(_SCRIPT_DIR / CALIBRATION_FILE)
    camera_matrix, dist_coeffs, _, _ = camera.calibrate(
        chessboard_size=(CHESSBOARD_COLS, CHESSBOARD_ROWS),
        square_size=SQUARE_SIZE_CM,
        num_images=NUM_CALIB_IMAGES,
        save_path=save_path,
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
        use_grayscale = not SHOW_CAMERA_FEED
        camera = CSICamera(CAMERA_ID, grayscale=use_grayscale)

        # Charger calibration : .npz d'abord, puis .env en fallback
        cam_matrix = CAMERA_MATRIX
        dist_coeffs = DIST_COEFFS
        file_mtx, file_dist = load_calibration_file()
        if file_mtx is not None:
            cam_matrix, dist_coeffs = file_mtx, file_dist

        # Initialiser l'undistortion si calibration disponible
        effective_camera_matrix = cam_matrix
        if cam_matrix is not None and dist_coeffs is not None:
            effective_camera_matrix = camera.init_undistort_maps(
                cam_matrix, dist_coeffs,
                alpha=parse_float("UNDISTORT_ALPHA", 0.0),
            )

        print("🔍 Initialisation du détecteur ArUco...")
        detector = ArucoDetector(
            camera,
            camera_matrix=effective_camera_matrix,
            dist_coeffs=None,  # Plus de distorsion après undistort
            assumed_hfov_deg=ASSUMED_HFOV_DEG,
        )
        # Configuration détection avancée depuis .env
        detector.multiscale_enabled = parse_bool("MULTISCALE_DETECTION", True)
        detector.multiscale_min_markers = parse_int(
            "MULTISCALE_MIN_MARKERS", 50,
        )
        if parse_bool("TEMPORAL_SMOOTHING", True):
            detector.marker_carry_frames = parse_int(
                "MARKER_CARRY_FRAMES", 2,
            )
        else:
            detector.marker_carry_frames = 0
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
    match_state = MatchState()

    if not DUMMY_LORA:
        print("📡 Initialisation de la carte LoRa...")
        lora = LoRa(
            port="/dev/ttyTHS1",
            baudrate=115200,
        )
        try:
            lora.connect()
        except RuntimeError as e:
            print(f"❌ LoRa indisponible: {e}")
            sys.exit(1)

        if not lora.is_healthy:
            print("❌ LoRa non sain après connect() — abandon.")
            sys.exit(1)

        # --- Handlers LoRa entrants ---
        def on_id_request(_args):
            pid = match_state.register_pami()
            lora.queue_send(f"2|{pid}\n")
            print(f"🤖 PAMI enregistré: id={pid}")

        def on_match_start(args):
            if not args:
                print("msg 4 reçu sans couleur — ignoré")
                return
            if match_state.start_match(args[0]):
                print(f"🏁 Match démarré, team={args[0]}")

        lora.register_handler(1, on_id_request)
        lora.register_handler(4, on_match_start)

        lora.start()
    else:
        print("📡 LoRa désactivé (DUMMY_LORA=True)")

    # Compteurs FPS
    frame_count = 0
    start_time = time.time()
    fps_display = 0.0

    # Créer les fenêtres / writers GStreamer
    gst_writer = None
    if SHOW_CAMERA_FEED and not DUMMY_DETECTION:
        if HAS_DISPLAY:
            cv2.namedWindow("ArUco Detection", cv2.WINDOW_NORMAL)
        else:
            # Si un serveur d'affichage tourne (X/Wayland), nvdrmvideosink
            # échoue car il ne peut pas devenir DRM master. On privilégie
            # nv3dsink/nvoverlaysink (fenêtre X) dans ce cas.
            has_x_session = bool(
                os.environ.get("DISPLAY")
                or os.environ.get("WAYLAND_DISPLAY"),
            )
            if has_x_session:
                gst_sinks = ["nv3dsink", "nvoverlaysink", "nvdrmvideosink"]
            else:
                gst_sinks = ["nvdrmvideosink", "nv3dsink", "nvoverlaysink"]
            for sink_name in gst_sinks:
                gst_pipeline = (
                    "appsrc ! videoconvert ! "
                    f"video/x-raw, width={GST_DISPLAY_WIDTH},"
                    f" height={GST_DISPLAY_HEIGHT},"
                    f" framerate={GST_DISPLAY_FPS}/1,"
                    " format=I420 ! "
                    f"{sink_name} sync=false"
                )
                gst_writer = cv2.VideoWriter(
                    gst_pipeline,
                    cv2.CAP_GSTREAMER,
                    0,
                    GST_DISPLAY_FPS,
                    (GST_DISPLAY_WIDTH, GST_DISPLAY_HEIGHT),
                    True,
                )
                if gst_writer.isOpened():
                    print(
                        f"🖥️  Affichage via {sink_name}",
                    )
                    break
                gst_writer = None
            if gst_writer is None:
                print(
                    "⚠️  Aucun sink GStreamer"
                    " disponible pour l'affichage",
                )
    if HAS_DISPLAY and SHOW_ARENA:
        cv2.namedWindow("Arena", cv2.WINDOW_NORMAL)

    # Historique des positions robots pour le calcul de vitesse
    robot_position_history = {
        ROBOT_MARKER_ID: deque(maxlen=SPEED_HISTORY_SIZE),
        ENEMY_MARKER_ID: deque(maxlen=SPEED_HISTORY_SIZE),
    }

    # État partagé pour le thread clavier
    latest_detected_world = []
    latest_robot_speeds = {}
    state_lock = threading.Lock()

    def _get_detected_world():
        with state_lock:
            return list(latest_detected_world)

    def _get_robot_speeds():
        with state_lock:
            return dict(latest_robot_speeds)

    # Lancer le thread clavier si LoRa actif
    kb_stop = None
    if lora is not None:
        kb_stop = start_keyboard_thread(
            lora, match_state, _get_detected_world, _get_robot_speeds,
        )
        print(
            "⌨️  Commandes clavier actives : "
            "2=ID PAMI, 3=dépôts, 5=vision (1/4=réception seule)",
        )

    print("🚀 Démarrage de la détection...")

    try:
        while True:
            if not DUMMY_DETECTION:
                # Lire la frame et corriger la distorsion
                frame = camera.read_frame(copy=SHOW_CAMERA_FEED)
                if frame is None:
                    continue
                frame = camera.undistort_frame(frame)

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
            if SHOW_CAMERA_FEED and annotated_frame is not None:
                cv2.putText(
                    annotated_frame,
                    f"FPS: {fps_display:.1f}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    (0, 255, 0),
                    2,
                )
                if HAS_DISPLAY:
                    cv2.imshow("ArUco Detection", annotated_frame)
                elif gst_writer is not None:
                    gst_writer.write(annotated_frame)

            # Affichage markers debug
            if DEBUG_MODE and detected_world:
                for marker_id, pos, yaw in detected_world:
                    print(
                        f"   ID={marker_id} | ",
                        f"Pos=({pos[0]:.3f}, {pos[1]:.3f})m | ",
                        f"Angle={math.degrees(yaw):.1f}°",
                    )

            # Tracking vitesse robots
            robot_speeds = {}
            for marker_id, pos, _yaw in detected_world:
                if marker_id in robot_position_history:
                    robot_position_history[marker_id].append(
                        (current_time, float(pos[0]), float(pos[1])),
                    )
                    robot_speeds[marker_id] = compute_speed(
                        robot_position_history[marker_id],
                    )

            # Mise à jour état partagé pour le thread clavier
            with state_lock:
                latest_detected_world = detected_world
                latest_robot_speeds = robot_speeds

            # Msg 3 : à T+90s, envoyer les attributions de dépôts aux PAMIs (une seule fois)
            if match_state.should_send_pre_end():
                assignments = match_state.compute_depot_assignments(arena_elements)
                msg3 = MatchState.build_msg_3(assignments)
                if lora is not None:
                    lora.queue_send(msg3)
                elif DEBUG_MODE:
                    print(f"[DUMMY_LORA] {msg3.strip()}")
                match_state.mark_pre_end_sent()
                print(f"📨 msg 3 envoyé: {len(assignments)} PAMI(s) assignés")

            # Msg 5 : envoi continu pendant le match uniquement
            if match_state.match_started and not match_state.is_over():
                msg = build_lora_message(
                    detected_world, robot_speeds, ZONE_TOLERANCE_M,
                )
                if lora is not None:
                    lora.queue_send(msg)
                elif DEBUG_MODE:
                    print(f"[DUMMY_LORA] {msg.strip()}")

            # Gestion des touches (uniquement si fenêtres OpenCV ouvertes)
            if HAS_DISPLAY and (
                (SHOW_CAMERA_FEED and not DUMMY_DETECTION) or SHOW_ARENA
            ):
                key = cv2.waitKey(1) & 0xFF
                if key == 27 or key == ord("q"):
                    break

    finally:
        print("\n🛑 Arrêt de la détection")
        if kb_stop is not None:
            kb_stop.set()
        plt.close("all")
        if camera is not None:
            camera.release()
        if HAS_DISPLAY:
            cv2.destroyAllWindows()
        if gst_writer is not None:
            gst_writer.release()
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
