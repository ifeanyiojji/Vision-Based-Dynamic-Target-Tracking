"""OpenCV-based tracking helpers."""

from collections.abc import Sequence

import cv2
import numpy as np


class TargetTracker:
    """Track a user-selected bounding box with an OpenCV correlation tracker."""

    _TRACKERS = ("CSRT", "KCF", "MOSSE")

    def __init__(self, frame: np.ndarray, bbox: Sequence[float]) -> None:
        self._tracker, self.name = self._create_tracker()
        initialized = self._tracker.init(frame, tuple(round(v) for v in bbox))
        if initialized is False:
            raise RuntimeError("OpenCV could not initialize the target tracker")

    @classmethod
    def _create_tracker(cls):
        for name in cls._TRACKERS:
            factory = getattr(cv2, f"Tracker{name}_create", None)
            if factory is None:
                legacy = getattr(cv2, "legacy", None)
                factory = getattr(legacy, f"Tracker{name}_create", None)
            if factory is not None:
                return factory(), name
        raise RuntimeError(
            "No supported OpenCV tracker is available. Install opencv-contrib-python."
        )

    def update(self, frame: np.ndarray) -> tuple[bool, tuple[int, int, int, int] | None]:
        """Return whether the target was found and its current bounding box."""
        found, bbox = self._tracker.update(frame)
        if not found:
            return False, None
        x, y, width, height = bbox
        return True, (round(x), round(y), round(width), round(height))
