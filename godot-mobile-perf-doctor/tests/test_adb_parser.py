import unittest

from godot_mobile_perf_doctor.adb_parser import parse_adb_summary


class AdbParserTests(unittest.TestCase):
    def test_parses_mocked_adb_summary(self) -> None:
        summary = parse_adb_summary(
            """
Device: Pixel 8
Android: 15
Total frames rendered: 120
Janky frames: 6 (5.0%)
"""
        )

        self.assertEqual(summary.device, "Pixel 8")
        self.assertEqual(summary.android, "15")
        self.assertEqual(summary.total_frames, 120)
        self.assertEqual(summary.janky_frames, 6)


if __name__ == "__main__":
    unittest.main()
