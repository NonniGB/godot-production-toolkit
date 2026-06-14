import tempfile
import unittest
from pathlib import Path

from PIL import Image

from pixel_space_assets.compare import compare_directories, compare_images, compare_manifests
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

    def test_compare_images_marks_changed_pixels(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            baseline = root / "baseline.png"
            current = root / "current.png"
            diff = root / "diff.png"
            Image.new("RGBA", (3, 3), (1, 1, 1, 255)).save(baseline)
            changed = Image.new("RGBA", (3, 3), (1, 1, 1, 255))
            changed.putpixel((2, 2), (100, 100, 100, 255))
            changed.save(current)

            result = compare_images(baseline, current, diff)

            self.assertEqual(result.different_pixels, 1)
            self.assertFalse(result.size_mismatch)
            with Image.open(diff) as diff_image:
                self.assertEqual(diff_image.getpixel((2, 2)), (255, 74, 92, 255))

    def test_compare_directories_keeps_relative_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            baseline = root / "baseline"
            current = root / "current"
            diff_dir = root / "diffs"
            (baseline / "tiles").mkdir(parents=True)
            (current / "tiles").mkdir(parents=True)
            Image.new("RGBA", (2, 2), (1, 1, 1, 255)).save(baseline / "tiles" / "a.png")
            Image.new("RGBA", (2, 2), (2, 2, 2, 255)).save(current / "tiles" / "a.png")

            result = compare_directories(baseline, current, diff_dir)

            self.assertEqual(result.changed_files, 1)
            self.assertTrue((diff_dir / "tiles" / "a.png").exists())
            self.assertEqual(result.entries[0]["path"], "tiles/a.png")

    def test_compare_manifests_uses_manifest_file_list(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            baseline = root / "baseline"
            current = root / "current"
            diff_dir = root / "diffs"
            baseline.mkdir()
            current.mkdir()
            Image.new("RGBA", (2, 2), (1, 1, 1, 255)).save(baseline / "tile.png")
            Image.new("RGBA", (2, 2), (1, 1, 1, 255)).save(current / "tile.png")
            (baseline / "manifest.json").write_text(
                '{"type":"asteroid-hex","seed":1,"tiles":[{"file":"tile.png"}]}',
                encoding="utf-8",
            )
            (current / "manifest.json").write_text(
                '{"type":"asteroid-hex","seed":2,"tiles":[{"file":"tile.png"}]}',
                encoding="utf-8",
            )

            result = compare_manifests(
                baseline / "manifest.json",
                current / "manifest.json",
                diff_dir,
            )

            self.assertEqual(result.unchanged_files, 1)
            self.assertEqual(result.manifest_changes, [{"field": "seed", "baseline": 1, "current": 2}])


if __name__ == "__main__":
    unittest.main()
