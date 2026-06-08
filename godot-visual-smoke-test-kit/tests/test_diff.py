import tempfile
import unittest
from pathlib import Path

from PIL import Image

from godot_visual_smoke.diff import compare_images


class DiffTests(unittest.TestCase):
    def test_compare_images_counts_changed_pixels_and_writes_diff(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            baseline = root / "baseline.png"
            current = root / "current.png"
            diff = root / "diff.png"
            Image.new("RGBA", (2, 2), (0, 0, 0, 255)).save(baseline)
            image = Image.new("RGBA", (2, 2), (0, 0, 0, 255))
            image.putpixel((1, 1), (255, 0, 0, 255))
            image.save(current)

            result = compare_images(baseline, current, diff_path=diff, pixel_tolerance=0, max_changed_percent=0)

            self.assertFalse(result.passed)
            self.assertEqual(result.changed_pixels, 1)
            self.assertAlmostEqual(result.changed_percent, 25.0)
            self.assertTrue(diff.exists())

    def test_compare_images_passes_with_pixel_tolerance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            baseline = root / "baseline.png"
            current = root / "current.png"
            Image.new("RGBA", (1, 1), (10, 10, 10, 255)).save(baseline)
            Image.new("RGBA", (1, 1), (11, 10, 10, 255)).save(current)

            result = compare_images(baseline, current, pixel_tolerance=1, max_changed_percent=0)

            self.assertTrue(result.passed)
            self.assertEqual(result.changed_pixels, 0)


if __name__ == "__main__":
    unittest.main()
