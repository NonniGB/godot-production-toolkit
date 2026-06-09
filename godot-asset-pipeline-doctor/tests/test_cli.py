from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys
import tempfile
import unittest

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from godot_asset_doctor.cli import main


class CliTests(unittest.TestCase):
    def test_cli_prints_version(self) -> None:
        stdout = StringIO()

        with self.assertRaises(SystemExit) as raised:
            with redirect_stdout(stdout):
                main(["--version"])

        self.assertEqual(raised.exception.code, 0)
        self.assertIn("godot-asset-doctor 0.1.3", stdout.getvalue())

    def test_cli_outputs_json_report_and_returns_failure_when_warning_threshold_is_used(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project = Path(tmp_dir)
            image_path = project / "assets" / "sprite.png"
            image_path.parent.mkdir()
            image = Image.new("RGBA", (2, 2), (0, 0, 0, 0))
            pixels = image.load()
            pixels[0, 0] = (255, 0, 0, 0)
            pixels[1, 1] = (10, 10, 10, 255)
            image.save(image_path)
            image_path.with_suffix(".png.import").write_text(
                "\n".join(
                    [
                        "[params]",
                        "mipmaps/generate=true",
                        "process/fix_alpha_border=false",
                    ]
                ),
                encoding="utf-8",
            )

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        str(project),
                        "--profile",
                        "pixel-2d",
                        "--format",
                        "json",
                        "--fail-on",
                        "warning",
                    ]
                )

            report = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 1)
            self.assertEqual(report["summary"]["asset_count"], 1)
            self.assertGreaterEqual(report["summary"]["warning_count"], 1)
            self.assertIn("transparent_edge_rgb", {issue["code"] for issue in report["issues"]})

    def test_cli_uses_toml_config_defaults_when_arguments_are_not_provided(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project = Path(tmp_dir)
            image_path = project / "assets" / "sprite.png"
            image_path.parent.mkdir()
            image = Image.new("RGBA", (2, 2), (0, 0, 0, 0))
            pixels = image.load()
            pixels[0, 0] = (255, 0, 0, 0)
            pixels[1, 1] = (10, 10, 10, 255)
            image.save(image_path)
            image_path.with_suffix(".png.import").write_text(
                "\n".join(
                    [
                        "[params]",
                        "mipmaps/generate=true",
                        "process/fix_alpha_border=false",
                    ]
                ),
                encoding="utf-8",
            )
            config_path = project / ".godot-asset-doctor.toml"
            config_path.write_text(
                "\n".join(
                    [
                        'profile = "pixel-2d"',
                        'format = "json"',
                        'fail_on = "warning"',
                        "max_palette_colors = 1",
                    ]
                ),
                encoding="utf-8",
            )

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main([str(project), "--config", str(config_path)])

            report = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 1)
            self.assertEqual(report["summary"]["profile"], "pixel-2d")
            self.assertIn("pixel_mipmaps_enabled", {issue["code"] for issue in report["issues"]})
            self.assertIn("large_palette", {issue["code"] for issue in report["issues"]})

    def test_cli_outputs_sarif_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project = Path(tmp_dir)
            image_path = project / "assets" / "sprite.png"
            image_path.parent.mkdir()
            Image.new("RGBA", (2, 2), (0, 0, 0, 0)).save(image_path)
            image_path.with_suffix(".png.import").write_text(
                "[params]\nmipmaps/generate=true\n",
                encoding="utf-8",
            )

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main([str(project), "--profile", "pixel-2d", "--format", "sarif", "--fail-on", "none"])

            sarif = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(sarif["version"], "2.1.0")
            driver = sarif["runs"][0]["tool"]["driver"]
            self.assertEqual(driver["name"], "godot-asset-pipeline-doctor")
            self.assertTrue(driver["rules"])
            self.assertTrue(sarif["runs"][0]["results"])

    def test_cli_creates_parent_directory_for_output_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project = Path(tmp_dir)
            output = project / "reports" / "assets" / "report.json"

            exit_code = main([str(project), "--format", "json", "--output", str(output), "--fail-on", "none"])

            self.assertEqual(exit_code, 0)
            self.assertTrue(output.exists())


if __name__ == "__main__":
    unittest.main()
