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

    def test_plan_cli_includes_viewport_manifest_safe_area(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / "visual-smoke.toml"
            manifest = root / "viewports.toml"
            manifest.write_text(
                """
[viewports.portrait_phone]
width = 720
height = 1280
safe_area = { top = 48, bottom = 24 }
""",
                encoding="utf-8",
            )
            config.write_text(
                """
[[scenes]]
name = "menu"
path = "res://scenes/menu.tscn"
viewport = "portrait_phone"
""",
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "plan",
                        str(config),
                        "--project",
                        str(root),
                        "--viewport-manifest",
                        str(manifest),
                        "--format",
                        "json",
                    ]
                )

            payload = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["commands"][0]["viewport"]["safe_area"]["top"], 48)
            self.assertEqual(payload["commands"][0]["viewport"]["safe_area"]["bottom"], 24)


if __name__ == "__main__":
    unittest.main()
