"""Simple MJPEG video streaming utilities."""

from video.server import MJPEGHandler, spawn_video_server

__all__ = [
    "MJPEGHandler",
    "spawn_video_server",
]
