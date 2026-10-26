import math
import unittest

from mobileaerial.control import ImageBasedServo, ServoConfig


class ImageBasedServoTests(unittest.TestCase):
    def setUp(self):
        self.controller = ImageBasedServo()

    def test_centered_target_at_desired_size_has_zero_commands(self):
        command = self.controller.compute((390, 190, 220, 220), (1000, 600))

        self.assertAlmostEqual(command.lateral, 0)
        self.assertAlmostEqual(command.vertical, 0)
        self.assertAlmostEqual(command.forward, 0)

    def test_target_to_right_and_below_produces_positive_lateral_and_vertical(self):
        command = self.controller.compute((650, 380, 100, 100), (1000, 600))

        self.assertGreater(command.lateral, 0)
        self.assertGreater(command.vertical, 0)

    def test_small_target_requests_forward_motion(self):
        command = self.controller.compute((450, 250, 100, 100), (1000, 600))

        self.assertGreater(command.forward, 0)
        self.assertAlmostEqual(command.size_error, math.log(2.2))

    def test_large_target_requests_backward_motion(self):
        command = self.controller.compute((350, 150, 300, 300), (1000, 600))

        self.assertLess(command.forward, 0)

    def test_commands_are_saturated(self):
        controller = ImageBasedServo(ServoConfig(max_command=0.25))
        command = controller.compute((900, 500, 20, 20), (1000, 600))

        self.assertLessEqual(abs(command.lateral), 0.25)
        self.assertLessEqual(abs(command.vertical), 0.25)
        self.assertLessEqual(abs(command.forward), 0.25)

    def test_invalid_inputs_are_rejected(self):
        with self.assertRaises(ValueError):
            self.controller.compute((0, 0, 10, 10), (0, 600))
        with self.assertRaises(ValueError):
            self.controller.compute((0, 0, 0, 10), (1000, 600))
        with self.assertRaises(ValueError):
            ServoConfig(desired_width_ratio=1.0)


if __name__ == "__main__":
    unittest.main()
