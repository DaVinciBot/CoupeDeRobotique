"""Threaded camera module for high-performance video capture."""

import threading
import time
from typing import Optional

import cv2
import numpy as np
from src.camera import Camera


class ThreadedCamera(Camera):
    """Camera class with threaded frame reading for better performance.

    This class continuously reads frames in a background thread, allowing
    the main thread to retrieve the latest frame without waiting for I/O.
    """

    def __init__(
        self,
        camera_id: int,
        width: Optional[int] = None,
        height: Optional[int] = None,
        backends: Optional[list] = None,
        buffer_size: int = 1,
        fps: Optional[float] = None,
    ) -> None:
        """Initialize the threaded camera.

        Args:
            camera_id (int): The ID of the camera to use.
            width (int, optional): The desired width of the camera feed.
            height (int, optional): The desired height of the camera feed.
            backends (list[int], optional): List of backend preferences.
            buffer_size (int): Number of frames to buffer (1 = latest only).
        """
        super().__init__(camera_id, width, height, backends, fps=fps)

        self.buffer_size = buffer_size
        self.frame = None
        self.frame_lock = threading.Lock()
        self.stopped = False
        self.thread = None

        # Statistiques de performance
        self.frames_read = 0
        self.frames_dropped = 0
        self.frames_consumed = 0  # Frames effectivement utilisées
        self.last_fps_time = time.time()
        self.fps = 0.0
        self.frame_was_read = True  # Flag pour tracker si frame a été lue

        if self.is_opened():
            self.start()

    def start(self) -> None:
        """Start the background thread for reading frames."""
        if self.thread is None or not self.thread.is_alive():
            self.stopped = False

            # Diagnostic caméra
            if self.cam is not None:
                actual_fps = self.cam.get(cv2.CAP_PROP_FPS)
                backend = (
                    self.cam.getBackendName()
                    if hasattr(self.cam, "getBackendName")
                    else "unknown"
                )
                print(f"📹 Caméra: Backend={backend}, FPS configuré={actual_fps:.1f}")

            # Laisser la caméra se stabiliser complètement avant de lancer le thread
            time.sleep(0.3)  # Temps de stabilisation supplémentaire

            self.thread = threading.Thread(target=self._update_frame, daemon=True)
            self.thread.start()

            # Attendre que la première frame soit disponible
            time.sleep(0.2)

    def _update_frame(self) -> None:
        """Background thread function that continuously reads frames."""
        consecutive_failures = 0
        max_consecutive_failures = 5  # Arrêter après 5 échecs consécutifs

        while not self.stopped:
            if self.cam is None or not self.cam.isOpened():
                print("⚠️  ThreadedCamera: Caméra fermée détectée")
                break

            try:
                ret, frame = self.cam.read()

                if ret:
                    consecutive_failures = 0  # Reset le compteur d'échecs
                    with self.frame_lock:
                        # Si la frame précédente n'a pas été lue, c'est un vrai drop
                        if self.frame is not None and not self.frame_was_read:
                            self.frames_dropped += 1
                        self.frame = frame
                        self.frame_was_read = False  # Nouvelle frame non encore lue
                        self.frames_read += 1

                    # Calculer le FPS de lecture
                    current_time = time.time()
                    if current_time - self.last_fps_time >= 1.0:
                        self.fps = self.frames_read / (
                            current_time - self.last_fps_time
                        )
                        self.frames_read = 0
                        self.last_fps_time = current_time
                else:
                    # Échec de lecture
                    consecutive_failures += 1
                    if consecutive_failures >= max_consecutive_failures:
                        print(
                            f"❌ ThreadedCamera: {consecutive_failures} échecs consécutifs, arrêt du thread"
                        )
                        break
                    # Petite pause si la lecture échoue
                    time.sleep(0.01)

            except cv2.error as e:
                consecutive_failures += 1
                print(f"❌ ThreadedCamera OpenCV error: {e}")
                if consecutive_failures >= max_consecutive_failures:
                    print("❌ Trop d'erreurs, arrêt du thread de lecture")
                    break
                time.sleep(0.01)
            except Exception as e:
                print(f"❌ ThreadedCamera unexpected error: {e}")
                break

    def read_frame(self) -> Optional[np.ndarray]:
        """Read the latest frame from the buffer.

        Returns:
            np.ndarray | None: The latest captured frame or None if unavailable.
        """
        with self.frame_lock:
            if self.frame is not None:
                self.frame_was_read = True  # Marquer comme lue
                self.frames_consumed += 1
                return self.frame.copy()
            return None

    def set_fps(self, fps: int) -> bool:
        """Change le FPS de la caméra dynamiquement (version threadée).

        Cette méthode arrête temporairement le thread de lecture,
        change le FPS, puis redémarre le thread.

        Args:
            fps: Le nouveau FPS à définir

        Returns:
            bool: True si le changement a réussi
        """
        if not self.is_opened():
            print("❌ Impossible de changer le FPS: caméra non ouverte")
            return False

        print(f"🔄 Changement du FPS vers {fps}... (arrêt thread)")

        # Arrêter le thread de lecture
        was_running = self.thread is not None and self.thread.is_alive()
        if was_running:
            self.stopped = True
            self.thread.join(timeout=1.0)
            print("   ⏸️  Thread de lecture arrêté")

        # Appeler la méthode parent pour changer le FPS
        success = super().set_fps(fps)

        # Redémarrer le thread si il tournait
        if was_running:
            self.stopped = False
            self.thread = threading.Thread(target=self._update_frame, daemon=True)
            self.thread.start()
            time.sleep(0.3)  # Stabilisation du thread
            print("   ▶️  Thread de lecture redémarré")

        return success

    def get_stats(self) -> dict:
        """Get camera performance statistics.

        Returns:
            dict: Statistics including FPS and dropped frames.
        """
        return {
            "read_fps": self.fps,
            "frames_dropped": self.frames_dropped,
            "frames_consumed": self.frames_consumed,
            "buffer_size": self.buffer_size,
        }

    def release(self) -> None:
        """Stop the background thread and release the camera."""
        self.stopped = True
        if self.thread is not None:
            self.thread.join(timeout=1.0)
        super().release()

    def __del__(self):
        """Ensure resources are released on deletion."""
        self.release()
