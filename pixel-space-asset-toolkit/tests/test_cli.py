import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import json

from pixel_space_assets.cli import main


class CliTests(unittest.TestCase):
    def test_cli_prints_version(self) -> None:
        stdout = StringIO()

        with self.assertRaises(SystemExit) as raised:
            with redirect_stdout(stdout):
                main(["--version"])

        self.assertEqual(raised.exception.code, 0)
        self.assertIn("pixel-space-assets 0.1.4", stdout.getvalue())

    def test_starfield_cli_writes_image_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "starfield.png"
            manifest = Path(tmp) / "manifest.json"

            exit_code = main(
                [
                    "starfield",
                    "--width",
                    "16",
                    "--height",
                    "16",
                    "--seed",
                    "5",
                    "--stars",
                    "5",
                    "--output",
                    str(output),
                    "--manifest",
                    str(manifest),
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(output.exists())
            self.assertTrue(manifest.exists())

    def test_starfield_cli_can_print_json_status_for_automation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "starfield.png"
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "starfield",
                        "--width",
                        "16",
                        "--height",
                        "16",
                        "--seed",
                        "5",
                        "--stars",
                        "5",
                        "--output",
                        str(output),
                        "--format",
                        "json",
                    ]
                )

            payload = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["status"], "ok")
            self.assertEqual(payload["command"], "starfield")
            self.assertTrue(payload["outputs"]["image"].endswith("starfield.png"))

    def test_cli_rejects_non_positive_dimensions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "starfield.png"

            with self.assertRaises(SystemExit) as raised:
                main(["starfield", "--width", "0", "--height", "16", "--seed", "5", "--output", str(output)])

            self.assertEqual(raised.exception.code, 2)

    def test_compare_cli_writes_diff_and_json_summary(self) -> None:
        from PIL import Image

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            baseline = root / "baseline.png"
            current = root / "current.png"
            diff = root / "diff.png"
            Image.new("RGBA", (4, 4), (10, 10, 10, 255)).save(baseline)
            changed = Image.new("RGBA", (4, 4), (10, 10, 10, 255))
            changed.putpixel((1, 1), (255, 0, 0, 255))
            changed.save(current)
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "compare",
                        str(baseline),
                        str(current),
                        "--diff-output",
                        str(diff),
                        "--format",
                        "json",
                    ]
                )

            payload = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertTrue(diff.exists())
            self.assertEqual(payload["command"], "compare")
            self.assertEqual(payload["comparison"]["different_pixels"], 1)

    def test_compare_cli_can_fail_when_pixels_change(self) -> None:
        from PIL import Image

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            baseline = root / "baseline.png"
            current = root / "current.png"
            diff = root / "diff.png"
            Image.new("RGBA", (2, 2), (0, 0, 0, 255)).save(baseline)
            Image.new("RGBA", (2, 2), (255, 0, 0, 255)).save(current)

            with redirect_stdout(StringIO()):
                exit_code = main(
                    [
                        "compare",
                        str(baseline),
                        str(current),
                        "--diff-output",
                        str(diff),
                        "--fail-on-diff",
                    ]
                )

            self.assertEqual(exit_code, 1)
            self.assertTrue(diff.exists())

    def test_compare_dir_cli_reports_changed_added_and_removed_files(self) -> None:
        from PIL import Image

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            baseline = root / "baseline"
            current = root / "current"
            diff_dir = root / "diffs"
            baseline.mkdir()
            current.mkdir()
            Image.new("RGBA", (2, 2), (10, 10, 10, 255)).save(baseline / "same.png")
            Image.new("RGBA", (2, 2), (10, 10, 10, 255)).save(current / "same.png")
            Image.new("RGBA", (2, 2), (10, 10, 10, 255)).save(baseline / "changed.png")
            Image.new("RGBA", (2, 2), (20, 20, 20, 255)).save(current / "changed.png")
            Image.new("RGBA", (2, 2), (1, 1, 1, 255)).save(baseline / "removed.png")
            Image.new("RGBA", (2, 2), (2, 2, 2, 255)).save(current / "added.png")
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "compare-dir",
                        str(baseline),
                        str(current),
                        "--diff-output-dir",
                        str(diff_dir),
                        "--format",
                        "json",
                    ]
                )

            payload = json.loads(stdout.getvalue())
            comparison = payload["comparison"]
            self.assertEqual(exit_code, 0)
            self.assertEqual(comparison["changed_files"], 1)
            self.assertEqual(comparison["added_files"], 1)
            self.assertEqual(comparison["removed_files"], 1)
            self.assertEqual(comparison["unchanged_files"], 1)
            self.assertTrue((diff_dir / "changed.png").exists())
            self.assertTrue((diff_dir / "added.png").exists())
            self.assertTrue((diff_dir / "removed.png").exists())

    def test_compare_manifest_cli_reports_manifest_and_pixel_changes(self) -> None:
        from PIL import Image

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            baseline = root / "baseline"
            current = root / "current"
            diff_dir = root / "diffs"
            baseline.mkdir()
            current.mkdir()
            Image.new("RGBA", (2, 2), (10, 10, 10, 255)).save(baseline / "ferric_000.png")
            Image.new("RGBA", (2, 2), (20, 20, 20, 255)).save(current / "ferric_000.png")
            (baseline / "manifest.json").write_text(
                json.dumps(
                    {
                        "type": "asteroid-hex",
                        "material": "ferric",
                        "count": 1,
                        "size": 2,
                        "seed": 7,
                        "tiles": [{"file": "ferric_000.png", "seed": 7}],
                    }
                ),
                encoding="utf-8",
            )
            (current / "manifest.json").write_text(
                json.dumps(
                    {
                        "type": "asteroid-hex",
                        "material": "ferric",
                        "count": 1,
                        "size": 2,
                        "seed": 8,
                        "tiles": [{"file": "ferric_000.png", "seed": 8}],
                    }
                ),
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "compare-manifest",
                        str(baseline / "manifest.json"),
                        str(current / "manifest.json"),
                        "--diff-output-dir",
                        str(diff_dir),
                        "--format",
                        "json",
                    ]
                )

            payload = json.loads(stdout.getvalue())
            comparison = payload["comparison"]
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["command"], "compare-manifest")
            self.assertEqual(comparison["changed_files"], 1)
            self.assertEqual(comparison["manifest_changes"][0]["field"], "seed")
            self.assertTrue((diff_dir / "ferric_000.png").exists())


if __name__ == "__main__":
    unittest.main()
