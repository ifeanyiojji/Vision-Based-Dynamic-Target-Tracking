"""Command-line entry point for the MobileAerial tracking demo."""

import argparse
import time

import cv2

from mobileaerial.control import ImageBasedServo, ServoCommand
from mobileaerial.demo import MovingTargetScene
from mobileaerial.tracking import TargetTracker


WINDOW_NAME = "MobileAerial - Dynamic Target Tracking & Visual Servoing"


def _parse_source(value: str):
    if value.lower() == "demo":
        return "demo"
    try:
        return int(value)
    except ValueError:
        return value


def _draw_overlay(frame, bbox, command, tracker_name: str) -> None:
    height, width = frame.shape[:2]
    center = (width // 2, height // 2)
    cv2.drawMarker(frame, center, (80, 220, 80), cv2.MARKER_CROSS, 24, 2)
    cv2.rectangle(frame, (center[0] - 2, 0), (center[0] + 2, height), (70, 70, 70), 1)
    cv2.rectangle(frame, (0, center[1] - 2), (width, center[1] + 2), (70, 70, 70), 1)
    x, y, box_width, box_height = bbox
    cv2.rectangle(frame, (x, y), (x + box_width, y + box_height), (0, 210, 255), 2)
    cv2.circle(frame, (x + box_width // 2, y + box_height // 2), 4, (0, 210, 255), -1)

    lines = [
        f"Tracker: {tracker_name} | Target: LOCKED",
        f"Image error (x,y): {command.image_error_x:+.3f}, {command.image_error_y:+.3f}",
        f"Camera request (lateral, vertical, forward): "
        f"{command.lateral:+.2f}, {command.vertical:+.2f}, {command.forward:+.2f}",
        "Select target: drag ROI | r: reselect | q / Esc: quit",
    ]
    for index, text in enumerate(lines):
        cv2.putText(
            frame,
            text,
            (16, 28 + index * 27),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.62,
            (245, 245, 245),
            2,
            cv2.LINE_AA,
        )


def _select_target(frame, initial_bbox=None):
    if initial_bbox is not None:
        return initial_bbox
    selection = cv2.selectROI(WINDOW_NAME, frame, showCrosshair=True, fromCenter=False)
    if selection[2] <= 0 or selection[3] <= 0:
        return None
    return selection


def run(source: str | int) -> int:
    scene = MovingTargetScene() if source == "demo" else None
    capture = None if scene else cv2.VideoCapture(source)
    if capture is not None and not capture.isOpened():
        raise RuntimeError(f"Could not open video source: {source}")

    controller = ImageBasedServo()
    tracker = None
    command = ServoCommand(0, 0, 0, 0, 0, 0) if scene else None
    previous_time = time.monotonic()
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

    try:
        while True:
            now = time.monotonic()
            dt = min(now - previous_time, 0.1)
            previous_time = now
            if scene:
                if command is not None:
                    scene.advance(command, dt)
                frame = scene.render()
            else:
                ok, frame = capture.read()
                if not ok:
                    break

            if tracker is None:
                initial_bbox = scene.initial_bbox if scene else None
                bbox = _select_target(frame, initial_bbox)
                if bbox is None:
                    if scene:
                        continue
                    break
                tracker = TargetTracker(frame, bbox)

            found, bbox = tracker.update(frame)
            if found and bbox is not None:
                command = controller.compute(bbox, (frame.shape[1], frame.shape[0]))
                _draw_overlay(frame, bbox, command, tracker.name)
            else:
                cv2.putText(
                    frame,
                    "Target lost - press r to select again, or q to quit",
                    (16, 35),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2,
                    cv2.LINE_AA,
                )

            cv2.imshow(WINDOW_NAME, frame)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                break
            if key == ord("r"):
                tracker = None
    finally:
        if capture is not None:
            capture.release()
        cv2.destroyAllWindows()
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Track a moving visual target and compute image-based servo requests."
    )
    parser.add_argument(
        "--source",
        type=_parse_source,
        default="demo",
        help="demo, webcam index (e.g. 0), or a video file path (default: demo)",
    )
    args = parser.parse_args()
    try:
        raise SystemExit(run(args.source))
    except (RuntimeError, cv2.error) as error:
        parser.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    main()
