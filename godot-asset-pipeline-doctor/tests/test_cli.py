from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys
import tempfile
import unittest
import wave

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
        self.assertIn("godot-asset-doctor 0.1.9", stdout.getvalue())

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
            self.assertEqual(report["metadata"]["schema_version"], "1.2")
            self.assertEqual(report["metadata"]["tool_version"], "0.1.9")
            self.assertEqual(report["summary"]["asset_count"], 1)
            self.assertGreaterEqual(report["summary"]["warning_count"], 1)
            self.assertIn("transparent_edge_rgb", {issue["code"] for issue in report["issues"]})
            transparent_edge = next(issue for issue in report["issues"] if issue["code"] == "transparent_edge_rgb")
            self.assertEqual(transparent_edge["title"], "Transparent edge RGB data")
            self.assertIn("bleed into visible edges", transparent_edge["explanation"])
            self.assertIn("transparent_edge_rgb", report["rules"])

    def test_cli_audio_mobile_profile_reports_audio_assets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project = Path(tmp_dir)
            audio_path = project / "audio" / "music.wav"
            audio_path.parent.mkdir()
            with wave.open(str(audio_path), "wb") as handle:
                handle.setnchannels(1)
                handle.setsampwidth(2)
                handle.setframerate(8000)
                handle.writeframes(b"\x00\x00" * 8000)

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        str(project),
                        "--profile",
                        "audio-mobile",
                        "--large-audio-mb",
                        "0.001",
                        "--max-audio-duration-seconds",
                        "0.5",
                        "--format",
                        "json",
                        "--fail-on",
                        "none",
                    ]
                )

            report = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(report["summary"]["image_asset_count"], 0)
            self.assertEqual(report["summary"]["audio_asset_count"], 1)
            self.assertEqual(report["audio_assets"][0]["audio"]["format"], "wav")
            issue_codes = {issue["code"] for issue in report["issues"]}
            self.assertIn("audio_file_large", issue_codes)
            self.assertIn("audio_duration_long", issue_codes)

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
            rule_names = {rule["name"] for rule in driver["rules"]}
            self.assertIn("Mipmaps enabled for pixel art", rule_names)
            self.assertTrue(sarif["runs"][0]["results"])

    def test_cli_creates_parent_directory_for_output_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project = Path(tmp_dir)
            output = project / "reports" / "assets" / "report.json"

            exit_code = main([str(project), "--format", "json", "--output", str(output), "--fail-on", "none"])

            self.assertEqual(exit_code, 0)
            self.assertTrue(output.exists())

    def test_cli_reports_invalid_config_as_usage_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project = Path(tmp_dir)
            config = project / ".godot-asset-doctor.toml"
            config.write_text("format = [", encoding="utf-8")

            with self.assertRaises(SystemExit) as raised:
                main([str(project), "--config", str(config)])

            self.assertEqual(raised.exception.code, 2)

    def test_cli_rejects_non_positive_numeric_limits(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project = Path(tmp_dir)
            cases = [
                ["--max-texture-dimension", "0"],
                ["--large-texture-mb", "0"],
                ["--max-palette-colors", "0"],
                ["--large-audio-mb", "0"],
                ["--max-audio-duration-seconds", "0"],
            ]

            for extra_args in cases:
                with self.subTest(extra_args=extra_args):
                    with self.assertRaises(SystemExit) as raised:
                        main([str(project), *extra_args])

                    self.assertEqual(raised.exception.code, 2)

    def test_manifest_check_reports_anchor_and_dimension_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project = Path(tmp_dir)
            image_path = project / "assets" / "ship.png"
            image_path.parent.mkdir()
            Image.new("RGBA", (4, 4), (0, 0, 0, 255)).save(image_path)
            manifest = project / "sprite-manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "sprites": [
                            {
                                "id": "ship",
                                "source_path": "assets/ship.png",
                                "width": 5,
                                "height": 4,
                                "anchors": {
                                    "muzzle": {"x": 6, "y": 2},
                                    "center": {"x": 2, "y": 2},
                                },
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["manifest", "check", str(manifest), "--project", str(project), "--format", "json"])

            report = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 1)
            codes = {issue["code"] for issue in report["issues"]}
            self.assertIn("sprite_width_mismatch", codes)
            self.assertIn("sprite_anchor_out_of_bounds", codes)
            self.assertEqual(report["summary"]["anchors_checked"], 2)

    def test_manifest_check_passes_for_valid_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project = Path(tmp_dir)
            image_path = project / "assets" / "ship.png"
            image_path.parent.mkdir()
            Image.new("RGBA", (4, 4), (0, 0, 0, 255)).save(image_path)
            manifest = project / "sprite-manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "sprites": [
                            {
                                "id": "ship",
                                "source_path": "assets/ship.png",
                                "width": 4,
                                "height": 4,
                                "anchors": [{"name": "center", "x": 2, "y": 2}],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["manifest", "check", str(manifest), "--project", str(project)])

            self.assertEqual(exit_code, 0)
            self.assertIn("No sprite manifest issues found.", stdout.getvalue())

    def test_manifest_contact_sheet_writes_png_with_anchor_markers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project = Path(tmp_dir)
            image_path = project / "assets" / "ship.png"
            image_path.parent.mkdir()
            Image.new("RGBA", (8, 8), (0, 0, 0, 0)).save(image_path)
            manifest = project / "sprite-manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "sprites": [
                            {
                                "id": "ship",
                                "source_path": "assets/ship.png",
                                "width": 8,
                                "height": 8,
                                "anchors": {"muzzle": {"x": 6, "y": 4}},
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            output = project / "reports" / "sprites.png"
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "manifest",
                        "contact-sheet",
                        str(manifest),
                        "--project",
                        str(project),
                        "--output",
                        str(output),
                        "--thumb-size",
                        "32",
                        "--format",
                        "json",
                    ]
                )

            report = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertTrue(output.exists())
            self.assertEqual(report["summary"]["sprites_rendered"], 1)
            self.assertEqual(report["summary"]["anchors_rendered"], 1)
            with Image.open(output) as sheet:
                self.assertGreater(sheet.width, 0)
                self.assertGreater(sheet.height, 0)

    def test_manifest_overlays_write_one_png_per_sprite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project = Path(tmp_dir)
            image_path = project / "assets" / "ship.png"
            image_path.parent.mkdir()
            Image.new("RGBA", (8, 8), (0, 0, 0, 0)).save(image_path)
            manifest = project / "sprite-manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "sprites": [
                            {
                                "id": "ship/main",
                                "source_path": "assets/ship.png",
                                "width": 8,
                                "height": 8,
                                "anchors": {"muzzle": {"x": 6, "y": 4}},
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            output_dir = project / "reports" / "overlays"
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "manifest",
                        "overlays",
                        str(manifest),
                        "--project",
                        str(project),
                        "--output-dir",
                        str(output_dir),
                        "--scale",
                        "3",
                        "--format",
                        "json",
                    ]
                )

            report = json.loads(stdout.getvalue())
            overlay = output_dir / "ship_main.png"
            self.assertEqual(exit_code, 0)
            self.assertTrue(overlay.exists())
            self.assertEqual(report["summary"]["sprites_rendered"], 1)
            self.assertEqual(report["summary"]["anchors_rendered"], 1)
            with Image.open(overlay) as image:
                self.assertEqual(image.size, (24, 24))


if __name__ == "__main__":
    unittest.main()
