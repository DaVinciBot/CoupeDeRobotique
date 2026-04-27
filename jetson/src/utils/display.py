"""Helper d'affichage GStreamer pour Jetson Nano.

Sur la Jetson, OpenCV (build JetPack) est souvent compilé sans GTK/Qt
fiable, donc cv2.imshow plante (GTK init fail) ou affiche à 2 FPS.
On utilise un cv2.VideoWriter avec un pipeline GStreamer qui termine
sur un sink local (xvimagesink / nv3dsink / ximagesink / autovideosink),
avec fallback automatique entre sinks.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Optional

import cv2


def ensure_x_session() -> bool:
    """Détecte une session X/Wayland et restaure DISPLAY/XAUTHORITY si
    perdus (cas sudo / SSH). Si on tourne en sudo et qu'X tourne,
    autorise root via xhost.

    Returns:
        True si une session X/Wayland est disponible, False sinon.
    """
    x_socket_dir = Path("/tmp/.X11-unix")  # noqa: S108
    x_socket_exists = (
        any(x_socket_dir.glob("X*"))
        if x_socket_dir.exists()
        else False
    )
    try:
        xorg_running = subprocess.run(
            ["pgrep", "-x", "Xorg"],
            check=False,
            capture_output=True,
            timeout=1,
        ).returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        xorg_running = False

    has_x_session = bool(
        os.environ.get("DISPLAY")
        or os.environ.get("WAYLAND_DISPLAY")
        or x_socket_exists
        or xorg_running,
    )
    if not has_x_session:
        return False

    sudo_user = os.environ.get("SUDO_USER")
    target_user = sudo_user or os.environ.get("USER", "dvb")

    if not os.environ.get("DISPLAY"):
        os.environ["DISPLAY"] = ":0"
    if not os.environ.get("XAUTHORITY"):
        for xauth in (
            "/run/user/1000/gdm/Xauthority",
            f"/home/{target_user}/.Xauthority",
        ):
            if Path(xauth).exists():
                os.environ["XAUTHORITY"] = xauth
                break

    if sudo_user:
        for cmd in (
            ["sudo", "-u", sudo_user, "xhost", "+SI:localuser:root"],
            ["sudo", "-u", sudo_user, "xhost", "+local:root"],
        ):
            try:
                subprocess.run(
                    cmd,
                    check=False,
                    capture_output=True,
                    timeout=2,
                )
            except (subprocess.SubprocessError, FileNotFoundError):
                pass

    return True


def make_display_writer(
    width: int,
    height: int,
    fps: int,
    render_width: Optional[int] = None,
    render_height: Optional[int] = None,
) -> Optional[cv2.VideoWriter]:
    """Construit un cv2.VideoWriter GStreamer pour afficher en local.

    Tente plusieurs sinks dans l'ordre xvimagesink → nv3dsink →
    ximagesink → autovideosink (ou nv3dsink → autovideosink si pas de
    session X). Fait l'env recovery via ensure_x_session().

    Args:
        width: largeur du flux source (BGR) écrit dans le writer.
        height: hauteur du flux source.
        fps: framerate déclaré.
        render_width: largeur du sink (downscale). Défaut = width // 2.
        render_height: hauteur du sink. Défaut = height // 2.

    Returns:
        Un cv2.VideoWriter ouvert, ou None si aucun sink n'a pu s'ouvrir.
    """
    has_x_session = ensure_x_session()

    if render_width is None:
        render_width = width // 2
    if render_height is None:
        render_height = height // 2

    caps_in = (
        f"video/x-raw, format=BGR,"
        f" width={width},"
        f" height={height},"
        f" framerate={fps}/1"
    )
    scale = (
        f"videoscale ! video/x-raw,"
        f" width={render_width},"
        f" height={render_height}"
    )
    sink_pipelines = {
        "xvimagesink": (
            f"appsrc is-live=true format=time ! {caps_in} ! "
            f"videoconvert ! {scale} ! "
            "video/x-raw, format=I420 ! "
            "xvimagesink sync=false"
        ),
        "nv3dsink": (
            f"appsrc is-live=true format=time ! {caps_in} ! "
            "nvvidconv ! "
            f"video/x-raw(memory:NVMM), format=NV12,"
            f" width={render_width},"
            f" height={render_height} ! "
            "nv3dsink sync=false"
        ),
        "ximagesink": (
            f"appsrc is-live=true format=time ! {caps_in} ! "
            f"videoconvert ! {scale} ! "
            "video/x-raw, format=BGRx ! "
            "ximagesink sync=false"
        ),
        "autovideosink": (
            f"appsrc is-live=true format=time ! {caps_in} ! "
            f"videoconvert ! {scale} ! "
            "autovideosink sync=false"
        ),
    }
    if has_x_session:
        sink_order = [
            "xvimagesink",
            "nv3dsink",
            "ximagesink",
            "autovideosink",
        ]
    else:
        sink_order = ["nv3dsink", "autovideosink"]

    for sink_name in sink_order:
        candidate = cv2.VideoWriter(
            sink_pipelines[sink_name],
            cv2.CAP_GSTREAMER,
            0,
            fps,
            (width, height),
            True,
        )
        if candidate.isOpened():
            print(f"🖥️  Affichage via {sink_name}")
            return candidate

    return None
