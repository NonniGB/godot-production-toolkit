from contextlib import redirect_stdout
from io import StringIO
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from godot_visual_smoke.cli import main


class CliTests(unittest.TestCase):
    def test_cli_prints_version(self) -> None:
        stdout = StringIO()

        with self.assertRaises(SystemExit) as raised:
            with redirect_stdout(stdout):
                main(["--version"])

        self.assertEqual(raised.exception.code, 0)
        self.assertIn("godot-visual-smoke 0.1.0", stdout.getvalue())

    def test_compare_cli_writes_json_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            baseline = root / "baseline.png"
            current = root / "current.png"
            output = root / "report.json"
            Image.new("RGBA", (1, 1), (0, 0, 0, 255)).save(baseline)
            Image.new("RGBA", (1, 1), (255, 255, 255, 255)).save(current)

            exit_code = main(
                [
                    "compare",
                    str(baseline),
                    str(current),
                    "--format",
                    "json",
                    "--output",
                    str(output),
                ]
            )

            self.assertEqual(exit_code, 1)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["changed_pixels"], 1)


if __name__ == "__main__":
    unittest.main()
