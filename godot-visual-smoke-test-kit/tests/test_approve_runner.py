import tempfile
import unittest
import json
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from godot_visual_smoke.cli import main
from godot_visual_smoke.approve import approve_baseline
from godot_visual_smoke.runner import build_godot_command


class ApproveRunnerTests(unittest.TestCase):
    def test_approve_copies_current_to_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            current = root / "current.png"
            baseline = root / "baselines" / "menu.png"
            current.write_bytes(b"png-data")

            approve_baseline(current, baseline)

            self.assertEqual(baseline.read_bytes(), b"png-data")

    def test_builds_godot_command(self) -> None:
        command = build_godot_command(
            godot=Path("Godot.exe"),
            project=Path("project"),
            scene="res://scenes/menu.tscn",
            width=720,
            height=1280,
            output=Path("out/menu.png"),
        )

        self.assertIn("--path", command)
        self.assertIn("project", command)
        self.assertIn("--resolution", command)
        self.assertIn("720x1280", command)

    def test_plan_cli_can_emit_json_for_automation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / "visual-smoke.toml"
            project = root / "project"
            project.mkdir()
            config.write_text(
                """
[viewports.phone]
width = 720
height = 1280

[[scenes]]
name = "menu"
path = "res://scenes/menu.tscn"
viewport = "phone"
""",
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["plan", str(config), "--project", str(project), "--format", "json"])

            payload = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["commands"][0]["scene"], "res://scenes/menu.tscn")
            self.assertEqual(payload["commands"][0]["viewport"]["width"], 720)


if __name__ == "__main__":
    unittest.main()
