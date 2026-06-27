from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
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

    def test_missing_config_returns_actionable_usage_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing-doctor.toml"
            stderr = StringIO()

            with self.assertRaises(SystemExit) as raised:
                with redirect_stderr(stderr):
                    main(["plan", str(missing)])

            self.assertEqual(raised.exception.code, 2)
            rendered = stderr.getvalue()
            self.assertIn("Config file not found", rendered)
            self.assertIn("godot-project-doctor init --dry-run", rendered)
            self.assertIn("--project and --checks", rendered)

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
            (root / "reports" / "runtime-telemetry.csv").write_text("frame_ms,memory_mb\n16,128\n", encoding="utf-8")

            inspect_stdout = StringIO()
            with redirect_stdout(inspect_stdout):
                self.assertEqual(main(["inspect", str(root), "--format", "json"]), 0)
            inspected = json.loads(inspect_stdout.getvalue())
            self.assertTrue(inspected["features"]["export_presets"])
            self.assertTrue(inspected["features"]["png_assets"])
            self.assertTrue(inspected["features"]["content_data_likely"])
            self.assertTrue(inspected["features"]["runtime_telemetry_likely"])
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
            self.assertIn("runtime_telemetry", recommended)
            export = next(item for item in recommendation_payload["recommendations"] if item["id"] == "export")
            self.assertEqual(export["priority"], "high")
            self.assertEqual(export["package"], "godot-export-preset-doctor")
            self.assertEqual(export["install"], "python -m pip install godot-export-preset-doctor")
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

    def test_plan_includes_runtime_telemetry_when_path_is_configured(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / "godot-project-doctor.toml"
            config.write_text(
                """
[project]
path = "demo"
checks = ["runtime_telemetry"]

[tools.runtime_telemetry]
path = "reports/runtime"
""",
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                self.assertEqual(main(["plan", str(config), "--format", "json"]), 0)

            payload = json.loads(stdout.getvalue())
            command = payload["commands"][0]
            self.assertEqual(command["id"], "runtime_telemetry")
            self.assertEqual(command["argv"][0], "godot-telemetry-lab")
            self.assertIn("summarize", command["argv"])
            self.assertIn("reports", " ".join(command["argv"]))
            self.assertIn("--format", command["argv"])
            self.assertIn("--output", command["argv"])

    def test_plan_includes_pack_mod_when_manifest_is_configured(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / "godot-project-doctor.toml"
            config.write_text(
                """
[project]
path = "demo"
checks = ["pack_mod"]

[tools.pack_mod]
manifest = "pack-manifest.json"
base = "base-content.json"
allow_overrides = true
""",
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                self.assertEqual(main(["plan", str(config), "--format", "json"]), 0)

            payload = json.loads(stdout.getvalue())
            command = payload["commands"][0]
            self.assertEqual(command["id"], "pack_mod")
            self.assertEqual(command["argv"][0], "godot-pack-mod-doctor")
            self.assertIn("check", command["argv"])
            self.assertIn("pack-manifest.json", " ".join(command["argv"]))
            self.assertIn("--base", command["argv"])
            self.assertIn("base-content.json", " ".join(command["argv"]))
            self.assertIn("--allow-overrides", command["argv"])

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
            self.assertIn("Godot release evidence", rendered)
            self.assertFalse((root / "godot-project-doctor.toml").exists())

    def test_doctor_profile_outputs_first_run_guidance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "project.godot").write_text("[application]\nconfig/name=\"Tiny\"\n", encoding="utf-8")
            stdout = StringIO()

            with redirect_stdout(stdout):
                self.assertEqual(main(["doctor", str(root), "--profile", "mobile", "--format", "json"]), 0)

            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["kind"], "doctor_profile")
            self.assertEqual(payload["profile"], "mobile")
            self.assertIn("Mobile review", payload["title"])
            task_ids = [task["id"] for task in payload["tasks"]]
            self.assertEqual(task_ids, ["export", "mobile_perf", "input", "mobile_ui", "visual_smoke"])
            mobile_ui = next(task for task in payload["tasks"] if task["id"] == "mobile_ui")
            self.assertEqual(mobile_ui["status"], "needs_setup")
            self.assertIn("mobile UI metadata", " ".join(mobile_ui["expected_inputs"]))
            self.assertEqual(mobile_ui["package"], "godot-mobile-ui-doctor")
            self.assertEqual(mobile_ui["install"], "python -m pip install godot-mobile-ui-doctor")
            self.assertIn("godot-mobile-ui-doctor", mobile_ui["command"])
            self.assertIn("guided_plan", payload)
            self.assertIn(
                "python -m pip install godot-export-preset-doctor godot-mobile-perf-doctor godot-input-map-auditor godot-mobile-ui-doctor godot-visual-smoke-test-kit",
                payload["guided_plan"]["install_commands"],
            )
            profile_packages = {item["package"] for item in payload["guided_plan"]["packages"]}
            self.assertIn("godot-visual-smoke-test-kit", profile_packages)
            self.assertIn("godot-release-dashboard build", " ".join(payload["guided_plan"]["commands"]))
            self.assertFalse((root / "reports" / "godot-project-doctor" / "mobile-plan.md").exists())

    def test_doctor_profile_catalog_includes_focused_workflows(self) -> None:
        cases = {
            "android": ["export", "mobile_perf", "input", "assets", "localization"],
            "html5": ["export", "assets", "input", "localization", "visual_smoke"],
            "localization": ["localization", "mobile_ui", "visual_smoke", "input"],
            "runtime": ["scenario_report", "runtime_telemetry", "mobile_perf", "visual_smoke", "signals"],
            "mods": ["pack_mod", "content_graph", "scenario_report", "assets", "save_schema"],
            "save-migration": ["save_schema", "scenario_report", "content_graph", "runtime_telemetry"],
            "architecture": ["architecture", "signals", "api_comments", "scenario_report"],
            "visual": ["visual_smoke", "mobile_ui", "assets", "localization", "input"],
            "mobile-ui": ["input", "mobile_ui", "localization", "visual_smoke", "mobile_perf"],
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "project.godot").write_text("[application]\nconfig/name=\"Tiny\"\n", encoding="utf-8")
            for profile, expected in cases.items():
                stdout = StringIO()
                with redirect_stdout(stdout):
                    self.assertEqual(main(["doctor", str(root), "--profile", profile, "--format", "json"]), 0)
                payload = json.loads(stdout.getvalue())
                self.assertEqual(payload["profile"], profile)
                self.assertEqual([task["id"] for task in payload["tasks"]], expected)

            mods_stdout = StringIO()
            with redirect_stdout(mods_stdout):
                self.assertEqual(main(["doctor", str(root), "--profile", "mods", "--format", "json"]), 0)
            mods_payload = json.loads(mods_stdout.getvalue())
            pack_task = next(task for task in mods_payload["tasks"] if task["id"] == "pack_mod")
            self.assertEqual(pack_task["status"], "needs_setup")
            self.assertEqual(pack_task["package"], "godot-pack-mod-doctor")
            self.assertIn("pack manifest JSON", " ".join(pack_task["expected_inputs"]))
            self.assertIn("godot-pack-mod-doctor check", pack_task["command"])

    def test_unknown_doctor_profile_returns_usage_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            with self.assertRaises(SystemExit) as raised:
                main(["doctor", str(root), "--profile", "unknown-profile"])

            self.assertEqual(raised.exception.code, 2)


    def test_doctor_profile_text_outputs_install_guidance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "project.godot").write_text("[application]\nconfig/name=\"Tiny\"\n", encoding="utf-8")
            stdout = StringIO()

            with redirect_stdout(stdout):
                self.assertEqual(main(["doctor", str(root), "--profile", "release"]), 0)

            rendered = stdout.getvalue()
            self.assertIn("Install:", rendered)
            self.assertIn("python -m pip install godot-export-preset-doctor", rendered)
            self.assertIn("Package: godot-export-preset-doctor", rendered)

    def test_doctor_profile_writes_workflow_only_when_requested(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "project.godot").write_text("[application]\nconfig/name=\"Tiny\"\n", encoding="utf-8")
            workflow = root / ".github" / "workflows" / "content-checks.yml"
            stdout = StringIO()

            with redirect_stdout(stdout):
                self.assertEqual(
                    main(
                        [
                            "doctor",
                            str(root),
                            "--profile",
                            "content",
                            "--write-workflow",
                            "--workflow-path",
                            ".github/workflows/content-checks.yml",
                        ]
                    ),
                    0,
                )

            self.assertTrue(workflow.exists())
            workflow_text = workflow.read_text(encoding="utf-8")
            self.assertIn("Godot release evidence", workflow_text)
            self.assertIn("content_graph,save_schema,scenario_report,pack_mod,assets", workflow_text)
            self.assertIn("Workflow written:", stdout.getvalue())

    def test_doctor_profile_writes_guided_plan_only_when_requested(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "Tiny Project"
            root.mkdir()
            (root / "project.godot").write_text("[application]\nconfig/name=\"Tiny\"\n", encoding="utf-8")
            plan_path = root / "docs" / "mobile-plan.md"
            stdout = StringIO()

            with redirect_stdout(stdout):
                self.assertEqual(
                    main(
                        [
                            "doctor",
                            str(root),
                            "--profile",
                            "mobile",
                            "--reports-dir",
                            "reports/mobile checks",
                            "--write-plan",
                            "--plan-path",
                            "docs/mobile-plan.md",
                        ]
                    ),
                    0,
                )

            self.assertTrue(plan_path.exists())
            plan_text = plan_path.read_text(encoding="utf-8")
            self.assertIn("# Mobile review First-Run Plan", plan_text)
            self.assertIn("## Install", plan_text)
            self.assertIn(
                "python -m pip install godot-export-preset-doctor godot-mobile-perf-doctor godot-input-map-auditor godot-mobile-ui-doctor godot-visual-smoke-test-kit",
                plan_text,
            )
            self.assertIn("| `mobile_ui` | `godot-mobile-ui-doctor` | `godot-mobile-ui-doctor` |", plan_text)
            self.assertIn("- Package: `godot-mobile-ui-doctor`", plan_text)
            self.assertIn("## Suggested Commands", plan_text)
            self.assertIn("godot-project-doctor run --project", plan_text)
            self.assertIn('--reports-dir "reports/mobile checks"', plan_text)
            self.assertIn("godot-release-dashboard build", plan_text)
            self.assertIn("## Starter Config Preview", plan_text)
            self.assertIn("## GitHub Actions Preview", plan_text)
            self.assertNotIn(str(root), plan_text)
            self.assertIn("Plan written:", stdout.getvalue())

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
        self.assertIn("godot-project-doctor 0.2.1", stdout.getvalue())

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
        self.assertIn("godot-project-doctor 0.2.1", completed.stdout)


if __name__ == "__main__":
    unittest.main()
