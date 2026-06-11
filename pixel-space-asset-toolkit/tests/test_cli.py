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
        self.assertIn("pixel-space-assets 0.1.2", stdout.getvalue())

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


if __name__ == "__main__":
    unittest.main()
