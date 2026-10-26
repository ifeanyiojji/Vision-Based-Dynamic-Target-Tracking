import unittest

from mobileaerial.demo import MovingTargetScene
from mobileaerial.tracking import TargetTracker


class TargetTrackerTests(unittest.TestCase):
    def test_tracker_initializes_and_updates_on_demo_frame(self):
        scene = MovingTargetScene()
        frame = scene.render()
        tracker = TargetTracker(frame, scene.initial_bbox)

        found, bbox = tracker.update(frame)

        self.assertTrue(found)
        self.assertIsNotNone(bbox)
        self.assertIn(tracker.name, {"CSRT", "KCF", "MOSSE"})


if __name__ == "__main__":
    unittest.main()
