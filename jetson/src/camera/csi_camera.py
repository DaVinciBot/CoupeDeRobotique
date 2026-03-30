"""Simplified CSI camera module for Jetson Nano with IMX219."""

import threading
import time
from typing import Any, Dict, Optional, Tuple, Union

import cv2
import numpy as np

# Constantes de calibration
SHARPNESS_MIN_THRESHOLD = 50
COVERAGE_MAX_THRESHOLD = 2
MIN_IMAGES_FOR_CALIBRATION = 10
MEAN_EXCELLENT_CALIBRATION = 0.5
MEAN_BAD_CALIBRATION = 1.0

# Configuration CSI fixe (IMX219 sur Jetson Nano)
CSI_WIDTH = 1920
CSI_HEIGHT = 1080
CSI_FPS = 15


class CSICamera:
    """Caméra CSI threadée pour Jetson Nano (IMX219).

    Configuration fixe: 1920x1080 @ 15fps avec GStreamer.
    La lecture des frames se fait en continu dans un thread séparé.
    """

    def __init__(
        self,
        camera_id: int = 0,
        grayscale: bool = False,
    ) -> None:
        """Initialise la caméra CSI.

        Args:
            camera_id: ID de la caméra (0=CAM0, 1=CAM1 sur Jetson).
            grayscale: Si True, sort en GRAY8 directement via
                nvvidconv (GPU) au lieu de BGR (évite cvtColor CPU).
        """
        self.camera_id = camera_id
        self.grayscale = grayscale
        self.cam = None  # type: Optional[cv2.VideoCapture]

        # Thread pour lecture continue
        self.frame = None
        self.frame_lock = threading.Lock()
        self.stopped = False
        self.thread = None

        # Statistiques
        self.frames_read = 0
        self.frames_dropped = 0
        self.last_fps_time = time.time()
        self.read_fps = 0.0

        # Pipeline GStreamer pour IMX219
        if grayscale:
            gst_pipeline = (
                f"nvarguscamerasrc sensor-id={camera_id} ! "
                f"video/x-raw(memory:NVMM), "
                f"width={CSI_WIDTH}, height={CSI_HEIGHT}, "
                f"format=NV12, framerate={CSI_FPS}/1 ! "
                f"nvvidconv flip-method=0 ! "
                f"video/x-raw, width={CSI_WIDTH}, "
                f"height={CSI_HEIGHT}, format=GRAY8 ! "
                f"appsink"
            )
        else:
            gst_pipeline = (
                f"nvarguscamerasrc sensor-id={camera_id} ! "
                f"video/x-raw(memory:NVMM), "
                f"width={CSI_WIDTH}, height={CSI_HEIGHT}, "
                f"format=NV12, framerate={CSI_FPS}/1 ! "
                f"nvvidconv flip-method=0 ! "
                f"video/x-raw, width={CSI_WIDTH}, "
                f"height={CSI_HEIGHT}, format=BGRx ! "
                f"videoconvert ! "
                f"video/x-raw, format=BGR ! "
                f"appsink"
            )

        mode = "GRAY8" if grayscale else "BGR"
        print(
            f"🎥 CSI Camera {CSI_WIDTH}x{CSI_HEIGHT}"
            f" @ {CSI_FPS}fps ({mode})",
        )

        self.cam = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)

        if not self.is_opened():
            raise RuntimeError("❌ Échec ouverture caméra CSI")

        # Vider le buffer initial
        for _ in range(5):
            self.cam.read()
            time.sleep(0.01)

        # Démarrer le thread de lecture
        self._start_thread()

    def _start_thread(self) -> None:
        """Démarre le thread de lecture continue des frames."""
        self.stopped = False
        time.sleep(0.3)  # Stabilisation
        self.thread = threading.Thread(target=self._read_loop, daemon=True)
        self.thread.start()
        time.sleep(0.2)  # Attendre première frame

    def _read_loop(self) -> None:
        """Boucle de lecture continue (thread séparé)."""
        consecutive_failures = 0
        last_stats_time = time.time()
        frames_since_stats = 0

        while not self.stopped:
            if self.cam is None or not self.cam.isOpened():
                print("⚠️  Caméra fermée détectée")
                break

            try:
                ret, new_frame = self.cam.read()

                if ret:
                    consecutive_failures = 0
                    with self.frame_lock:
                        # Si frame précédente pas encore lue, on la drop
                        if self.frame is not None:
                            self.frames_dropped += 1
                        self.frame = new_frame
                        self.frames_read += 1
                        frames_since_stats += 1

                    # Calcul FPS lecture (toutes les secondes)
                    current_time = time.time()
                    if current_time - last_stats_time >= 1.0:
                        self.read_fps = frames_since_stats / (
                            current_time - last_stats_time
                        )
                        frames_since_stats = 0
                        last_stats_time = current_time
                else:
                    consecutive_failures += 1
                    if consecutive_failures >= 5:
                        print("❌ Trop d'échecs de lecture consécutifs")
                        break
                    time.sleep(0.01)

            except Exception as e:
                print(f"❌ Erreur lecture frame: {e}")
                consecutive_failures += 1
                if consecutive_failures >= 5:
                    break
                time.sleep(0.01)

        self.stopped = True

    def is_opened(self) -> bool:
        """Vérifie si la caméra est ouverte."""
        return self.cam is not None and self.cam.isOpened()

    def read_frame(self, copy: bool = True) -> Optional[np.ndarray]:
        """Récupère la dernière frame disponible.

        Args:
            copy: Si True, retourne une copie de la frame (nécessaire si on
                  dessine dessus). Si False, retourne la référence directe et
                  marque la frame comme consommée (plus rapide, ~2-3ms économisés).

        Returns:
            La frame la plus récente ou None si non disponible.
        """
        if not self.is_opened():
            return None

        with self.frame_lock:
            if self.frame is None:
                return None
            if copy:
                return self.frame.copy()
            # Swap atomique : on prend la référence, le thread caméra
            # créera un nouvel objet numpy au prochain cam.read()
            result = self.frame
            self.frame = None
            return result

    def get_stats(self) -> Dict[str, Union[int, float]]:
        """Retourne les statistiques de performance."""
        return {
            "frames_read": self.frames_read,
            "frames_dropped": self.frames_dropped,
            "read_fps": self.read_fps,
        }

    def get_resolution(self) -> Tuple[int, int]:
        """Retourne la résolution de la caméra."""
        return (CSI_WIDTH, CSI_HEIGHT)

    def get_camera_info(self) -> Dict[str, Union[int, float]]:
        """Retourne les informations de la caméra."""
        return {
            "width": CSI_WIDTH,
            "height": CSI_HEIGHT,
            "fps": CSI_FPS,
        }

    def calibrate(
        self,
        chessboard_size=(9, 6),  # type: Tuple[int, int]
        square_size=1.0,  # type: float
        num_images=20,  # type: int
    ):  # type: (...) -> Tuple[Optional[Any], Optional[Any], Optional[Any], Optional[Any]]
        """Calibre la caméra avec un échiquier.

        Args:
            chessboard_size: Nombre de coins intérieurs (cols, rows).
            square_size: Taille d'un carré (unité de votre choix).
            num_images: Nombre d'images à capturer.

        Returns:
            (camera_matrix, dist_coeffs, rvecs, tvecs) ou (None, None, None, None).
        """
        if not self.is_opened():
            return None, None, None, None

        # Points 3D de l'échiquier
        objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
        objp[:, :2] = np.mgrid[
            0 : chessboard_size[0],
            0 : chessboard_size[1],
        ].T.reshape(-1, 2)
        objp *= square_size

        objpoints, imgpoints = [], []
        captured = 0
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        # Carte de couverture pour garantir diversité des angles
        coverage_map = np.zeros((CSI_HEIGHT // 20, CSI_WIDTH // 20))

        print(f"\n📸 Capture de {num_images} images pour calibration")
        print("💡 CONSEILS: Variez angles, distances et positions")
        print("⌨️  'c' = capturer, 'q' = terminer\n")

        while captured < num_images:
            frame = self.read_frame()
            if frame is None:
                continue

            # Détection sur image réduite (4x plus rapide)
            small = cv2.resize(frame, None, fx=0.5, fy=0.5)
            gray_small = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)

            ret, corners = cv2.findChessboardCorners(
                gray_small,
                chessboard_size,
                cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE,
            )

            display = frame.copy()

            # Afficher la couverture
            coverage_display = cv2.resize(coverage_map, (200, 150))
            coverage_display = (
                coverage_display * 255 / max(1, coverage_map.max())
            ).astype(np.uint8)
            coverage_display = cv2.applyColorMap(coverage_display, cv2.COLORMAP_JET)
            display[10:160, 10:210] = coverage_display

            if ret and corners is not None:
                # Affiner les coins sur l'image pleine résolution
                corners = corners / 0.5
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)

                cv2.drawChessboardCorners(display, chessboard_size, corners, ret)

                # Mesure de netteté
                sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
                color = (
                    (0, 255, 0)
                    if sharpness > SHARPNESS_MIN_THRESHOLD
                    else (0, 165, 255)
                )

                cv2.putText(
                    display,
                    f"✓ Detecte! Nettete: {sharpness:.0f}",
                    (10, 180),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    color,
                    2,
                )
                cv2.putText(
                    display,
                    f"'c' pour capturer ({captured}/{num_images})",
                    (10, 210),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2,
                )
            else:
                cv2.putText(
                    display,
                    "✗ Pas de motif detecte",
                    (10, 180),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 0, 255),
                    2,
                )

            cv2.imshow("Calibration", display)
            key = cv2.waitKey(1) & 0xFF

            if key == ord("c") and ret:
                # Vérifier couverture
                center = np.mean(corners, axis=0)[0]
                grid_x = int(center[0] / 20)
                grid_y = int(center[1] / 20)

                if coverage_map[grid_y, grid_x] > COVERAGE_MAX_THRESHOLD:
                    print("⚠️  Zone déjà capturée, variez la position")
                    continue

                objpoints.append(objp)
                imgpoints.append(corners)
                coverage_map[grid_y, grid_x] += 1
                captured += 1
                print(f"✓ Image {captured}/{num_images} capturée")

            elif key == ord("q"):
                break

        cv2.destroyAllWindows()

        if captured < MIN_IMAGES_FOR_CALIBRATION:
            print(f"❌ Minimum {MIN_IMAGES_FOR_CALIBRATION} images nécessaires")
            return None, None, None, None

        print("\n🔄 Calibration en cours...")

        # Calibration avec contraintes (point principal fixé, aspect ratio fixé)
        flags = cv2.CALIB_FIX_PRINCIPAL_POINT + cv2.CALIB_FIX_ASPECT_RATIO

        ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
            objpoints,
            imgpoints,
            (CSI_WIDTH, CSI_HEIGHT),
            None,
            None,
            flags=flags,
        )

        if ret:
            # Calcul de l'erreur de reprojection
            total_error = 0
            for i in range(len(objpoints)):
                imgpoints2, _ = cv2.projectPoints(
                    objpoints[i],
                    rvecs[i],
                    tvecs[i],
                    camera_matrix,
                    dist_coeffs,
                )
                error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2) / len(
                    imgpoints2
                )
                total_error += error

            mean_error = total_error / len(objpoints)
            print(f"📊 Erreur de reprojection moyenne: {mean_error:.3f} pixels")

            if mean_error > MEAN_BAD_CALIBRATION:
                print("⚠️  ATTENTION: Erreur élevée, recommencez la calibration")
            elif mean_error < MEAN_EXCELLENT_CALIBRATION:
                print("✅ Excellente calibration!")
            else:
                print("✓ Calibration acceptable")

        return (
            (camera_matrix, dist_coeffs, rvecs, tvecs)
            if ret
            else (None, None, None, None)
        )

    def release(self) -> None:
        """Libère les ressources de la caméra."""
        self.stopped = True
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        if self.cam:
            self.cam.release()
            self.cam = None
