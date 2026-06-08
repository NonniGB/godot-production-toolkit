import tempfile
import unittest
from pathlib import Path

from PIL import Image

from godot_mobile_perf_doctor.textures import scan_textures


class TextureTests(unittest.TestCase):
    def test_large_texture_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            Image.new("RGBA", (4096, 1024), (0, 0, 0, 0)).save(root / "wide.png")

            summary = scan_textures(root, max_dimension=2048)

            self.assertEqual(summary.total_textures, 1)
            self.assertEqual(summary.large_textures[0].path.name, "wide.png")


if __name__ == "__main__":
    unittest.main()
