from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from godot_project_doctor.cli import main


class ProjectDoctorCliTests(unittest.TestCase):
    def test_plan_json_lists_enabled_and_disabled_tools(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / "godot-project-doctor.toml"
            config.write_text(
                """
[project]
path = "demo"
checks = ["assets", "export", "visual_smoke"]

[tools.assets]
args = ["--profile", "pixel-2d"]

[tools.visual_smoke]
config = "visual-smoke.toml"
""",
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["plan", str(config), "--format", "json"])

            payload = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            enabled = {item["id"] for item in payload["checks"] if item["enabled"]}
            self.assertIn("assets", enabled)
            self.assertIn("export", enabled)
            self.assertIn("visual_smoke", enabled)
            self.assertIn("godot-asset-doctor", payload["commands"][0]["argv"][0])
            self.assertEqual(payload["project"], str((root / "demo").resolve()))

    def test_run_dry_run_json_is_side_effect_free(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "project"
            project.mkdir()
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "run",
                        "--project",
                        str(project),
                        "--checks",
                        "assets,export",
                        "--reports-dir",
                        str(root / "reports"),
                        "--dry-run",
                        "--format",
                        "json",
                    ]
                )

            payload = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["status"], "planned")
            self.assertEqual([item["id"] for item in payload["checks"] if item["enabled"]], ["assets", "export"])
            self.assertFalse((root / "reports").exists())

    def test_summarize_outputs_json_markdown_and_html(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            reports = Path(tmp)
            (reports / "assets.json").write_text(
                json.dumps(
                    {
                        "tool": "godot-asset-pipeline-doctor",
                        "summary": {"error_count": 1, "warning_count": 2},
                        "issues": [
                            {
                                "code": "large_texture",
                                "severity": "warning",
                                "path": "res://icon.png",
                                "message": "Texture is large.",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            (reports / "export.json").write_text(
                json.dumps(
                    {
                        "tool": "godot-export-preset-doctor",
                        "summary": {"errors": 0, "warnings": 1},
                        "findings": [
                            {
                                "rule_id": "missing_icon",
                                "severity": "warning",
                                "preset_name": "Android",
                                "message": "Icon is missing.",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            json_stdout = StringIO()
            with redirect_stdout(json_stdout):
                self.assertEqual(main(["summarize", str(reports), "--format", "json"]), 0)
            payload = json.loads(json_stdout.getvalue())
            self.assertEqual(payload["summary"]["errors"], 1)
            self.assertEqual(payload["summary"]["warnings"], 3)
            self.assertEqual(payload["summary"]["tools"], 2)

            markdown_stdout = StringIO()
            with redirect_stdout(markdown_stdout):
                self.assertEqual(main(["summarize", str(reports), "--format", "markdown"]), 0)
            self.assertIn("# Godot Project Doctor Report", markdown_stdout.getvalue())
            self.assertIn("| godot-asset-pipeline-doctor | 1 | 2 |", markdown_stdout.getvalue())

            html_stdout = StringIO()
            with redirect_stdout(html_stdout):
                self.assertEqual(main(["summarize", str(reports), "--format", "html"]), 0)
            self.assertIn("<title>Godot Project Doctor Report</title>", html_stdout.getvalue())
            self.assertIn("godot-export-preset-doctor", html_stdout.getvalue())
            self.assertIn("Top Findings", html_stdout.getvalue())
            self.assertIn("Texture is large.", html_stdout.getvalue())

    def test_version_flag_prints_package_version(self) -> None:
        stdout = StringIO()

        with self.assertRaises(SystemExit) as raised:
            with redirect_stdout(stdout):
                main(["--version"])

        self.assertEqual(raised.exception.code, 0)
        self.assertIn("godot-project-doctor 0.1.0", stdout.getvalue())

    def test_module_execution_prints_version(self) -> None:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")

        completed = subprocess.run(
            [sys.executable, "-m", "godot_project_doctor", "--version"],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )

        self.assertEqual(completed.returncode, 0)
        self.assertIn("godot-project-doctor 0.1.0", completed.stdout)


if __name__ == "__main__":
    unittest.main()
