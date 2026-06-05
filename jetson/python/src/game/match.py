"""État du match et attribution des zones de dépôt aux PAMIs."""

import threading
import time

import numpy as np

MATCH_DURATION = 100.0  # secondes
PRE_END_OFFSET = 10.0  # envoi msg 3 à (MATCH_DURATION - PRE_END_OFFSET)

_TEAM_TO_KEY = {"B": "blue", "Y": "yellow"}


class MatchState:
    """Centralise l'état du match (thread-safe)."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._pami_ids: list[int] = []
        self._next_pami_id = 1

        self._team_color: str | None = None
        self._match_started = False
        self._match_start_ts: float | None = None
        self._pre_end_sent = False

    # ---- PAMIs ----

    def register_pami(self) -> int:
        """Alloue un nouvel ID PAMI et le renvoie."""
        with self._lock:
            pid = self._next_pami_id
            self._next_pami_id += 1
            self._pami_ids.append(pid)
            return pid

    def pami_ids(self) -> list[int]:
        with self._lock:
            return list(self._pami_ids)

    # ---- Match lifecycle ----

    def start_match(self, color: str) -> bool:
        """Démarre le match. Idempotent : ignore les appels suivants."""
        with self._lock:
            if self._match_started:
                return False
            if color not in _TEAM_TO_KEY:
                print(f"MatchState: couleur inconnue '{color}', attendu 'B' ou 'Y'")
                return False
            self._team_color = color
            self._match_started = True
            self._match_start_ts = time.monotonic()
            return True

    @property
    def match_started(self) -> bool:
        with self._lock:
            return self._match_started

    @property
    def team_color(self) -> str | None:
        with self._lock:
            return self._team_color

    def elapsed(self) -> float:
        with self._lock:
            if self._match_start_ts is None:
                return 0.0
            return time.monotonic() - self._match_start_ts

    def is_over(self) -> bool:
        """True si le match est démarré et la durée écoulée."""
        with self._lock:
            if not self._match_started or self._match_start_ts is None:
                return False
            return (time.monotonic() - self._match_start_ts) >= MATCH_DURATION

    def should_send_pre_end(self) -> bool:
        """True si on doit envoyer msg 3 maintenant (une seule fois)."""
        with self._lock:
            if not self._match_started or self._pre_end_sent:
                return False
            if self._match_start_ts is None:
                return False
            elapsed = time.monotonic() - self._match_start_ts
            return elapsed >= (MATCH_DURATION - PRE_END_OFFSET)

    def mark_pre_end_sent(self) -> None:
        with self._lock:
            self._pre_end_sent = True

    # ---- Dépôts ----

    def compute_depot_assignments(
        self, arena_elements: dict
    ) -> list[tuple[int, float, float]]:
        """Attribue à chaque PAMI la zone de dépôt libre la plus proche de notre
        zone de départ. Renvoie [(pami_id, x, y), ...] dans l'ordre d'enregistrement."""
        with self._lock:
            color = self._team_color
            pami_ids = list(self._pami_ids)

        if color is None or not pami_ids:
            return []

        team_key = _TEAM_TO_KEY[color]
        start_pos = arena_elements["starting_zone"][team_key]["position"]
        depots = arena_elements["zone_depot"]

        # Tri glouton : dépôts triés par distance croissante à la zone de départ.
        depots_sorted = sorted(
            depots,
            key=lambda d: float(np.linalg.norm(d["position"] - start_pos)),
        )

        assignments: list[tuple[int, float, float]] = []
        for pid, depot in zip(pami_ids, depots_sorted):
            x = float(depot["position"][0])
            y = float(depot["position"][1])
            assignments.append((pid, x, y))
        return assignments

    @staticmethod
    def build_msg_3(assignments: list[tuple[int, float, float]]) -> str:
        """Construit `3|id1|x1|y1|id2|x2|y2|...\\n`."""
        parts = ["3"]
        for pid, x, y in assignments:
            parts.append(str(pid))
            parts.append(f"{x:.3f}")
            parts.append(f"{y:.3f}")
        return "|".join(parts) + "\n"
