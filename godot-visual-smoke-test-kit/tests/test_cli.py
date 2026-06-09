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
        self.assertIn("godot-visual-smoke 0.1.1", stdout.getvalue())

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

    def test_approve_cli_can_write_json_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            current = root / "current.png"
            baseline = root / "baselines" / "current.png"
            output = root / "reports" / "approve.json"
            Image.new("RGBA", (1, 1), (0, 0, 0, 255)).save(current)

            exit_code = main(["approve", str(current), str(baseline), "--format", "json", "--output", str(output)])

            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(exit_code, 0)
            self.assertTrue(baseline.exists())
            self.assertEqual(payload["status"], "ok")


if __name__ == "__main__":
    unittest.main()
