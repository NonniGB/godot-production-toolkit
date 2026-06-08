from pathlib import Path
import sys
import tempfile
import unittest

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from godot_asset_doctor.inspector import inspect_png


class PngInspectorTests(unittest.TestCase):
    def test_inspect_png_reports_alpha_palette_and_contaminated_transparent_edge(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            image_path = Path(tmp_dir) / "sprite.png"
            image = Image.new("RGBA", (3, 3), (0, 0, 0, 0))
            pixels = image.load()
            pixels[0, 0] = (255, 0, 0, 0)
            pixels[1, 1] = (10, 20, 30, 255)
            image.save(image_path)

            info = inspect_png(image_path)

            self.assertEqual(info.width, 3)
            self.assertEqual(info.height, 3)
            self.assertTrue(info.has_alpha)
            self.assertEqual(info.transparent_pixel_count, 8)
            self.assertEqual(info.contaminated_transparent_pixel_count, 1)
            self.assertEqual(info.contaminated_transparent_edge_pixel_count, 1)
            self.assertGreaterEqual(info.palette_color_count, 2)


if __name__ == "__main__":
    unittest.main()

