from pathlib import Path
import sys
import tempfile
import unittest

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from godot_asset_doctor.scanner import scan_project


class ScannerTests(unittest.TestCase):
    def test_scan_project_skips_default_non_asset_artifact_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project = Path(tmp_dir)
            self._write_png(project / "assets" / "sprite.png")
            self._write_png(project / "docs" / "screenshot.png")
            self._write_png(project / "test-results" / "capture.png")

            report = scan_project(project, profile="pixel-2d")

            self.assertEqual([asset.path.name for asset in report.assets], ["sprite.png"])

    def test_scan_project_honors_configurable_exclude_globs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project = Path(tmp_dir)
            self._write_png(project / "assets" / "keep.png")
            self._write_png(project / "assets" / "generated" / "skip.png")

            report = scan_project(project, profile="pixel-2d", exclude_globs=["assets/generated/**"])

            self.assertEqual([asset.path.name for asset in report.assets], ["keep.png"])

    def _write_png(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        image = Image.new("RGBA", (1, 1), (255, 255, 255, 255))
        image.save(path)


if __name__ == "__main__":
    unittest.main()

