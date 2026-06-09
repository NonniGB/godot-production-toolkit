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

    def test_inspect_and_recommend_detect_common_project_signals(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "project.godot").write_text(
                """
[application]
config/name="Tiny Project"

[input]
jump={
"deadzone": 0.5,
"events": []
}

[display]
window/size/viewport_width=720
window/handheld/orientation=1
""",
                encoding="utf-8",
            )
            (root / "export_presets.cfg").write_text("[preset.0]\nplatform=\"Android\"\n", encoding="utf-8")
            (root / "assets").mkdir()
            (root / "assets" / "icon.png").write_bytes(b"\x89PNG\r\n\x1a\n")
            (root / "scripts").mkdir()
            (root / "scripts" / "player.gd").write_text("extends Node\n", encoding="utf-8")
            (root / "data").mkdir()
            (root / "data" / "items.json").write_text("[]", encoding="utf-8")
            (root / "addons" / "gut").mkdir(parents=True)
            (root / "addons" / "gut" / "plugin.cfg").write_text("[plugin]\nname=\"GUT\"\n", encoding="utf-8")
            (root / "reports").mkdir()
            (root / "reports" / "mobile-ui.json").write_text("{}", encoding="utf-8")

            inspect_stdout = StringIO()
            with redirect_stdout(inspect_stdout):
                self.assertEqual(main(["inspect", str(root), "--format", "json"]), 0)
            inspected = json.loads(inspect_stdout.getvalue())
            self.assertTrue(inspected["features"]["export_presets"])
            self.assertTrue(inspected["features"]["png_assets"])
            self.assertTrue(inspected["features"]["content_data_likely"])
            self.assertEqual(inspected["details"]["project_name"], "Tiny Project")
            self.assertEqual(inspected["details"]["gdscript_count"], 1)
            self.assertIn("GUT", inspected["details"]["test_frameworks"])
            self.assertIn("scripts/player.gd", inspected["details"]["sample_paths"]["scripts"])
            self.assertIn("assets/icon.png", inspected["details"]["sample_paths"]["assets"])
            self.assertIn("export", inspected["suggested_checks"])

            recommend_stdout = StringIO()
            with redirect_stdout(recommend_stdout):
                self.assertEqual(main(["recommend", str(root), "--format", "json"]), 0)
            recommendation_payload = json.loads(recommend_stdout.getvalue())
            recommended = {item["id"] for item in recommendation_payload["recommendations"]}
            self.assertIn("export", recommended)
            self.assertIn("assets", recommended)
            self.assertIn("content_graph", recommended)
            self.assertIn("mobile_ui", recommended)
            self.assertIn("scenario_report", recommended)
            export = next(item for item in recommendation_payload["recommendations"] if item["id"] == "export")
            self.assertEqual(export["priority"], "high")
            self.assertIn("godot-project-doctor run --project", export["command"])
            mobile_ui = next(item for item in recommendation_payload["recommendations"] if item["id"] == "mobile_ui")
            self.assertIn("needs config", mobile_ui["config"])

    def test_plan_includes_mobile_ui_when_metadata_is_configured(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / "godot-project-doctor.toml"
            config.write_text(
                """
[project]
path = "demo"
checks = ["mobile_ui"]

[tools.mobile_ui]
metadata = "reports/mobile-ui.json"
""",
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                self.assertEqual(main(["plan", str(config), "--format", "json"]), 0)

            payload = json.loads(stdout.getvalue())
            command = payload["commands"][0]
            self.assertEqual(command["id"], "mobile_ui")
            self.assertIn("godot-mobile-ui-doctor", command["argv"][0])
            self.assertIn("mobile-ui.json", " ".join(command["argv"]))

    def test_init_dry_run_prints_config_without_writing_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "project.godot").write_text("[application]\nconfig/name=\"Tiny\"\n", encoding="utf-8")
            stdout = StringIO()

            with redirect_stdout(stdout):
                self.assertEqual(main(["init", str(root), "--dry-run", "--include-workflow"]), 0)

            rendered = stdout.getvalue()
            self.assertIn("godot-project-doctor.toml", rendered)
            self.assertIn("[project]", rendered)
            self.assertIn("Godot production checks", rendered)
            self.assertFalse((root / "godot-project-doctor.toml").exists())

    def test_explain_outputs_check_guidance(self) -> None:
        stdout = StringIO()

        with redirect_stdout(stdout):
            self.assertEqual(main(["explain", "content_graph"]), 0)

        self.assertIn("Content Graph Doctor", stdout.getvalue())
        self.assertIn("data-driven content", stdout.getvalue())

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

    def test_compare_reports_shows_deltas_and_can_fail_on_regressions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            baseline = root / "baseline"
            current = root / "current"
            baseline.mkdir()
            current.mkdir()
            (baseline / "assets.json").write_text(
                json.dumps(
                    {
                        "tool": "godot-asset-pipeline-doctor",
                        "summary": {"errors": 0, "warnings": 1},
                        "findings": [
                            {
                                "severity": "warning",
                                "message": "Texture could be smaller.",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            (current / "assets.json").write_text(
                json.dumps(
                    {
                        "tool": "godot-asset-pipeline-doctor",
                        "summary": {"errors": 1, "warnings": 2},
                        "findings": [
                            {
                                "severity": "error",
                                "message": "Texture import is missing.",
                            },
                            {
                                "severity": "warning",
                                "message": "Texture could be smaller.",
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )

            json_stdout = StringIO()
            with redirect_stdout(json_stdout):
                self.assertEqual(main(["compare", str(baseline), str(current), "--format", "json"]), 0)
            payload = json.loads(json_stdout.getvalue())
            self.assertEqual(payload["summary"]["regressions"], 1)
            self.assertEqual(payload["summary"]["error_delta"], 1)
            self.assertEqual(payload["summary"]["warning_delta"], 1)
            self.assertEqual(payload["comparisons"][0]["status"], "regressed")

            markdown_stdout = StringIO()
            with redirect_stdout(markdown_stdout):
                self.assertEqual(main(["compare", str(baseline), str(current), "--format", "markdown"]), 0)
            self.assertIn("# Godot Project Doctor Compare", markdown_stdout.getvalue())
            self.assertIn("| godot-asset-pipeline-doctor | regressed | +1 | +1 | +1 |", markdown_stdout.getvalue())

            with redirect_stdout(StringIO()):
                self.assertEqual(main(["compare", str(baseline), str(current), "--fail-on", "error"]), 1)

    def test_collect_writes_evidence_folder_from_existing_reports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reports = root / "reports"
            reports.mkdir()
            (reports / "mobile-ui.json").write_text(
                json.dumps(
                    {
                        "tool": "godot-mobile-ui-doctor",
                        "summary": {"errors": 0, "warnings": 1},
                        "findings": [
                            {
                                "rule_id": "touch_target_too_small",
                                "severity": "warning",
                                "message": "Button is small.",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            evidence = root / "evidence"
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "collect",
                        "--project",
                        str(root),
                        "--checks",
                        "mobile_ui",
                        "--reports-dir",
                        str(reports),
                        "--evidence-dir",
                        str(evidence),
                        "--skip-run",
                        "--fail-on",
                        "none",
                    ]
                )

            self.assertEqual(exit_code, 0)
            self.assertTrue((evidence / "manifest.json").exists())
            self.assertTrue((evidence / "summary.md").exists())
            self.assertTrue((evidence / "artifacts.json").exists())
            manifest = json.loads((evidence / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["summary"]["warnings"], 1)
            self.assertIn("summary.html", {path.name for path in evidence.iterdir()})

    def test_version_flag_prints_package_version(self) -> None:
        stdout = StringIO()

        with self.assertRaises(SystemExit) as raised:
            with redirect_stdout(stdout):
                main(["--version"])

        self.assertEqual(raised.exception.code, 0)
        self.assertIn("godot-project-doctor 0.1.4", stdout.getvalue())

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
        self.assertIn("godot-project-doctor 0.1.4", completed.stdout)


if __name__ == "__main__":
    unittest.main()
