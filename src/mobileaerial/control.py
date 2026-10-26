"""Image-based visual servoing for a camera-equipped aerial robot."""

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class ServoCommand:
    """Normalized camera-motion requests; these are not flight-controller units."""

    lateral: float
    vertical: float
    forward: float
    image_error_x: float
    image_error_y: float
    size_error: float


@dataclass(frozen=True)
class ServoConfig:
    """Controller targets and proportional gains."""

    desired_width_ratio: float = 0.22
    lateral_gain: float = 0.8
    vertical_gain: float = 0.8
    forward_gain: float = 0.7
    max_command: float = 1.0

    def __post_init__(self) -> None:
        if not 0 < self.desired_width_ratio < 1:
            raise ValueError("desired_width_ratio must be between 0 and 1")
        if min(self.lateral_gain, self.vertical_gain, self.forward_gain) < 0:
            raise ValueError("controller gains must not be negative")
        if self.max_command <= 0:
            raise ValueError("max_command must be positive")


class ImageBasedServo:
    """Center and maintain apparent target size using image-space feedback."""

    def __init__(self, config: ServoConfig | None = None) -> None:
        self.config = config or ServoConfig()

    def compute(
        self,
        bbox: tuple[float, float, float, float],
        frame_size: tuple[int, int],
    ) -> ServoCommand:
        """Return normalized motion requests for (x, y, width, height) and (w, h)."""
        x, y, width, height = bbox
        frame_width, frame_height = frame_size
        if frame_width <= 0 or frame_height <= 0:
            raise ValueError("frame dimensions must be positive")
        if width <= 0 or height <= 0:
            raise ValueError("bounding-box dimensions must be positive")

        center_x = (x + width / 2) / frame_width
        center_y = (y + height / 2) / frame_height
        error_x = center_x - 0.5
        error_y = center_y - 0.5
        width_ratio = width / frame_width
        size_error = math.log(self.config.desired_width_ratio / width_ratio)

        return ServoCommand(
            lateral=self._limit(self.config.lateral_gain * error_x),
            vertical=self._limit(self.config.vertical_gain * error_y),
            forward=self._limit(self.config.forward_gain * size_error),
            image_error_x=error_x,
            image_error_y=error_y,
            size_error=size_error,
        )

    def _limit(self, value: float) -> float:
        limit = self.config.max_command
        return max(-limit, min(limit, value))
