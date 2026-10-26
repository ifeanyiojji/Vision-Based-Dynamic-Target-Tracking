"""A camera-free scene for exercising the tracking and servoing loop."""

import math

import cv2
import numpy as np

from mobileaerial.control import ServoCommand


class MovingTargetScene:
    def __init__(self, width: int = 960, height: int = 540) -> None:
        self.width = width
        self.height = height
        self.elapsed = 0.0
        self.camera_x = 0.0
        self.camera_y = 0.0
        self.log_scale = 0.0

    @property
    def initial_bbox(self) -> tuple[int, int, int, int]:
        size = round(self.height * 0.22)
        return (self.width // 2 - size // 2, self.height // 2 - size // 2, size, size)

    def advance(self, command: ServoCommand, dt: float) -> None:
        self.elapsed += dt
        self.camera_x += command.lateral * 150 * dt
        self.camera_y += command.vertical * 120 * dt
        self.log_scale = max(-0.7, min(0.7, self.log_scale + command.forward * 0.5 * dt))

    def render(self) -> np.ndarray:
        frame = np.full((self.height, self.width, 3), 28, dtype=np.uint8)
        for x in range(0, self.width, 48):
            cv2.line(frame, (x, 0), (x, self.height), (38, 42, 48), 1)
        for y in range(0, self.height, 48):
            cv2.line(frame, (0, y), (self.width, y), (38, 42, 48), 1)

        center_x = round(
            self.width / 2
            + 145 * math.sin(self.elapsed * 0.65)
            - self.camera_x
        )
        center_y = round(
            self.height / 2
            + 78 * math.sin(self.elapsed * 0.91 + 0.7)
            - self.camera_y
        )
        radius = round(self.height * 0.11 * math.exp(self.log_scale))
        cv2.circle(frame, (center_x, center_y), radius + 5, (235, 210, 55), -1)
        cv2.circle(frame, (center_x, center_y), radius, (30, 125, 235), -1)
        cv2.circle(frame, (center_x, center_y), max(4, radius // 5), (245, 245, 245), -1)
        cv2.line(
            frame,
            (center_x - radius // 2, center_y),
            (center_x + radius // 2, center_y),
            (245, 245, 245),
            2,
        )
        return frame
