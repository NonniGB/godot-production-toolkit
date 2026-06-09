from pathlib import Path
import sys
import tempfile
import unittest
import wave

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

    def test_audio_mobile_profile_scans_audio_assets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project = Path(tmp_dir)
            self._write_png(project / "assets" / "sprite.png")
            self._write_wav(project / "audio" / "effect.wav")

            report = scan_project(project, profile="audio-mobile")

            self.assertEqual(report.assets, [])
            self.assertEqual([asset.path.name for asset in report.audio_assets], ["effect.wav"])
            self.assertEqual(report.summary()["audio_asset_count"], 1)
            self.assertIn("missing_audio_import_metadata", {issue.code for issue in report.issues})

    def _write_png(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        image = Image.new("RGBA", (1, 1), (255, 255, 255, 255))
        image.save(path)

    def _write_wav(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with wave.open(str(path), "wb") as handle:
            handle.setnchannels(1)
            handle.setsampwidth(2)
            handle.setframerate(8000)
            handle.writeframes(b"\x00\x00" * 800)


if __name__ == "__main__":
    unittest.main()
