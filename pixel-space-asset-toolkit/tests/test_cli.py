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
        self.assertIn("pixel-space-assets 0.1.0", stdout.getvalue())

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


if __name__ == "__main__":
    unittest.main()
