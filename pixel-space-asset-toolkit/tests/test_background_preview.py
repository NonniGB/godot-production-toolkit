import tempfile
import unittest
from pathlib import Path

from PIL import Image

from pixel_space_assets.preview import build_contact_sheet
from pixel_space_assets.strip_background import strip_background


class BackgroundPreviewTests(unittest.TestCase):
    def test_strip_background_makes_corner_color_transparent(self) -> None:
        image = Image.new("RGBA", (2, 2), (255, 0, 255, 255))
        image.putpixel((1, 1), (10, 20, 30, 255))

        stripped = strip_background(image, tolerance=0)

        self.assertEqual(stripped.getpixel((0, 0))[3], 0)
        self.assertEqual(stripped.getpixel((1, 1))[3], 255)

    def test_contact_sheet_dimensions_follow_columns(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for index in range(3):
                Image.new("RGBA", (8, 8), (index, index, index, 255)).save(root / f"{index}.png")

            sheet = build_contact_sheet(sorted(root.glob("*.png")), columns=2, cell_size=8)

            self.assertEqual(sheet.size, (16, 16))


if __name__ == "__main__":
    unittest.main()
