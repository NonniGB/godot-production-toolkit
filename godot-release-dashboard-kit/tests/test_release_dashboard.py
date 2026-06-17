from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from godot_release_dashboard_kit.cli import main
from godot_release_dashboard_kit.dashboard import build_dashboard


class ReleaseDashboardTests(unittest.TestCase):
    def test_builds_html_dashboard(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reports = root / "reports"
            reports.mkdir()
            (reports / "export.json").write_text(
                json.dumps({"tool": "godot-export-doctor", "summary": {"errors": 1, "warnings": 2}}),
                encoding="utf-8",
            )
            output = root / "dashboard.html"

            exit_code = main(["build", str(reports), "--output", str(output)])

            html = output.read_text(encoding="utf-8")
            self.assertEqual(exit_code, 0)
            self.assertIn("Godot Release Dashboard", html)
            self.assertIn("godot-export-doctor", html)
            self.assertIn("Errors: 1", html)
            self.assertIn("Visual Artifacts", html)

    def test_builds_json_dashboard(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reports = root / "reports"
            reports.mkdir()
            (reports / "notes.md").write_text("# Notes\n\nwarning: check this", encoding="utf-8")
            (reports / "overlay.svg").write_text(
                "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"120\" height=\"80\"><rect width=\"120\" height=\"80\" fill=\"#111827\"/></svg>",
                encoding="utf-8",
            )
            output = root / "dashboard.json"

            exit_code = main(["build", str(reports), "--format", "json", "--output", str(output)])

            data = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(exit_code, 0)
            self.assertEqual(data["tool_version"], "0.1.6")
            self.assertEqual(data["summary"]["reports"], 1)
            self.assertEqual(data["summary"]["images"], 1)
            self.assertEqual(data["summary"]["workflows"], 1)
            self.assertEqual(data["reports"][0]["workflow_id"], "general")
            self.assertEqual(data["images"][0]["mime"], "image/svg+xml")
            self.assertTrue(data["images"][0]["data_uri"].startswith("data:image/svg+xml;base64,"))

    def test_groups_reports_by_release_state_and_links_sources(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reports = root / "reports"
            reports.mkdir()
            blocked_report = reports / "export.json"
            blocked_report.write_text(
                json.dumps({"tool": "godot-export-doctor", "summary": {"errors": 2, "warnings": 0}}),
                encoding="utf-8",
            )
            attention_report = reports / "perf.json"
            attention_report.write_text(
                json.dumps({"tool": "godot-perf-check", "summary": {"errors": 0, "warnings": 1}}),
                encoding="utf-8",
            )
            ready_report = reports / "notes.md"
            ready_report.write_text("# Ship notes\n\nAll release notes checked.", encoding="utf-8")
            output = root / "dashboard.html"

            dashboard = build_dashboard(reports)
            exit_code = main(["build", str(reports), "--output", str(output)])

            html = output.read_text(encoding="utf-8")
            self.assertEqual(exit_code, 0)
            self.assertEqual(dashboard["summary"]["blocked"], 1)
            self.assertEqual(dashboard["summary"]["attention"], 1)
            self.assertEqual(dashboard["summary"]["ready"], 1)
            self.assertIn("Release Readiness", html)
            self.assertIn("Export and packaging", html)
            self.assertIn("General reports", html)
            self.assertIn("Workflows: 3", html)
            self.assertIn("Blocked: 1", html)
            self.assertIn("Needs attention: 1", html)
            self.assertIn("Ready: 1", html)
            self.assertIn('href="reports/export.json"', html)
            self.assertIn('href="reports/perf.json"', html)
            self.assertIn('href="reports/notes.md"', html)
            self.assertNotIn(str(root), html)

    def test_groups_reports_by_workflow(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reports = root / "reports"
            reports.mkdir()
            (reports / "export.json").write_text(
                json.dumps({"tool": "godot-export-preset-doctor", "kind": "export_matrix", "summary": {}}),
                encoding="utf-8",
            )
            (reports / "scenario.json").write_text(
                json.dumps({"tool": "godot-scenario-report-kit", "kind": "scenario_bundle", "summary": {"scenarios": 1}}),
                encoding="utf-8",
            )
            (reports / "architecture.json").write_text(
                json.dumps({"tool": "godot-gdscript-architecture-guard", "kind": "architecture", "summary": {}}),
                encoding="utf-8",
            )

            dashboard = build_dashboard(reports)
            workflows = {item["id"]: item for item in dashboard["workflows"]}

            self.assertEqual(dashboard["summary"]["workflows"], 3)
            self.assertEqual(workflows["export"]["label"], "Export and packaging")
            self.assertEqual(workflows["runtime"]["label"], "Runtime evidence")
            self.assertEqual(workflows["refactor"]["label"], "Refactor safety")
            by_tool = {report["tool"]: report for report in dashboard["reports"]}
            self.assertEqual(by_tool["godot-export-preset-doctor"]["workflow_label"], "Export and packaging")
            self.assertEqual(by_tool["godot-scenario-report-kit"]["workflow_label"], "Runtime evidence")

    def test_respects_report_workflow_and_category_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reports = root / "reports"
            reports.mkdir()
            (reports / "export.json").write_text(
                json.dumps(
                    {
                        "tool": "custom-export-check",
                        "workflow": "Release checklist",
                        "category": "Android export",
                        "summary": {"warnings": 1},
                    }
                ),
                encoding="utf-8",
            )
            (reports / "runtime.json").write_text(
                json.dumps(
                    {
                        "tool": "custom-runner",
                        "metadata": {"workflow": "Runtime evidence", "category": "JUnit"},
                        "summary": {},
                    }
                ),
                encoding="utf-8",
            )
            output = root / "dashboard.html"

            dashboard = build_dashboard(reports)
            exit_code = main(["build", str(reports), "--output", str(output)])

            workflows = {item["id"]: item for item in dashboard["workflows"]}
            html = output.read_text(encoding="utf-8")
            self.assertEqual(exit_code, 0)
            self.assertIn("release-checklist", workflows)
            self.assertIn("runtime-evidence", workflows)
            self.assertEqual(dashboard["reports"][0]["category"], "Android export")
            self.assertIn("Release checklist", html)
            self.assertIn("Android export", html)
            self.assertIn("Runtime evidence", html)
            self.assertIn("JUnit", html)

    def test_scenario_bundle_reports_reviewer_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reports = root / "reports"
            reports.mkdir()
            bundle_report = reports / "scenario-bundle.json"
            bundle_report.write_text(
                json.dumps(
                    {
                        "tool": "godot-scenario-report-kit",
                        "kind": "scenario_bundle",
                        "summary": {
                            "scenarios": 2,
                            "passed": 1,
                            "failed": 1,
                            "skipped": 0,
                            "errors": 0,
                            "warnings": 1,
                            "linked_evidence": 3,
                            "artifacts": 2,
                        },
                        "bundle": {
                            "telemetry_summary": {
                                "kind": "runtime_telemetry_timeline",
                                "relative_path": "../runtime-summary.json",
                                "samples": 18,
                                "frame_p95_ms": 21.5,
                                "frame_max_ms": 33.1,
                                "memory_max_mb": 256,
                                "spikes": 2,
                                "warnings": 1,
                                "errors": 0,
                            },
                            "links": {
                                "telemetry": {
                                    "kind": "telemetry",
                                    "relative_path": "../runtime-timeline.html",
                                    "exists": True,
                                    "size_bytes": 1200,
                                }
                            },
                            "evidence_links": [
                                {"kind": "log", "relative_path": "../run.log", "exists": True, "size_bytes": 240},
                                {"kind": "junit", "relative_path": "../junit.xml", "exists": False},
                            ],
                            "scenarios": [
                                {
                                    "scenario": "menu_startup",
                                    "bundle_artifacts": [
                                        {"path": "screenshots/menu.png", "exists": True},
                                        {"path": "logs/missing.txt", "exists": False},
                                    ],
                                }
                            ],
                        },
                    }
                ),
                encoding="utf-8",
            )

            dashboard = build_dashboard(reports)
            output = root / "dashboard.html"
            exit_code = main(["build", str(reports), "--output", str(output)])

            html = output.read_text(encoding="utf-8")
            self.assertEqual(exit_code, 0)
            self.assertEqual(dashboard["summary"]["scenario_bundles"], 1)
            self.assertEqual(dashboard["summary"]["scenarios"], 2)
            self.assertEqual(dashboard["summary"]["scenario_passed"], 1)
            self.assertEqual(dashboard["summary"]["scenario_failed"], 1)
            self.assertEqual(dashboard["summary"]["scenario_evidence"], 3)
            self.assertEqual(dashboard["summary"]["scenario_telemetry_bundles"], 1)
            self.assertEqual(dashboard["summary"]["scenario_telemetry_samples"], 18)
            self.assertEqual(dashboard["summary"]["scenario_telemetry_spikes"], 2)
            self.assertEqual(dashboard["summary"]["scenario_telemetry_warnings"], 1)
            self.assertEqual(dashboard["reports"][0]["status"], "blocked")
            scenario_bundle = dashboard["reports"][0]["scenario_bundle"]
            self.assertEqual(scenario_bundle["scenarios"], 2)
            self.assertEqual(scenario_bundle["passed"], 1)
            self.assertEqual(scenario_bundle["failed"], 1)
            self.assertEqual(scenario_bundle["evidence_count"], 3)
            self.assertEqual(scenario_bundle["artifact_count"], 2)
            self.assertEqual(scenario_bundle["missing_evidence"], 1)
            self.assertEqual(scenario_bundle["missing_artifacts"], 1)
            self.assertEqual(scenario_bundle["telemetry_summary"]["samples"], 18)
            self.assertEqual(scenario_bundle["telemetry_summary"]["frame_p95_ms"], 21.5)
            self.assertIn("Scenario Bundle Evidence", html)
            self.assertIn("Scenarios: 1 passed / 2 total", html)
            self.assertIn("Telemetry samples: 18", html)
            self.assertIn("Telemetry spikes: 2", html)
            self.assertIn("Telemetry: 18 samples", html)
            self.assertIn("frame p95 21.50 ms", html)
            self.assertIn("../runtime-timeline.html", html)
            self.assertIn("../run.log", html)
            self.assertIn("screenshots/menu.png", html)
            self.assertIn("Missing evidence: 1", html)

    def test_json_reports_surface_reproduction_commands_and_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reports = root / "reports"
            reports.mkdir()
            pack_report = reports / "pack-mod.json"
            pack_report.write_text(
                json.dumps(
                    {
                        "tool": "godot-pack-mod-doctor",
                        "tool_version": "0.1.4",
                        "schema_version": "1.0",
                        "kind": "pack_load_order",
                        "command": "godot-pack-mod-doctor load-order base.json patch.json --format json",
                        "generated_at": "2026-06-17T12:00:00Z",
                        "summary": {
                            "errors": 0,
                            "warnings": 1,
                            "risk_level": "attention",
                            "risk_score": 10,
                            "packs": 2,
                        },
                        "risk": {"level": "attention", "score": 10, "reasons": ["content_id_conflict"]},
                    }
                ),
                encoding="utf-8",
            )

            dashboard = build_dashboard(reports)
            output = root / "dashboard.html"
            exit_code = main(["build", str(reports), "--output", str(output)])

            html = output.read_text(encoding="utf-8")
            report = dashboard["reports"][0]
            self.assertEqual(exit_code, 0)
            self.assertEqual(dashboard["summary"]["reports_with_commands"], 1)
            self.assertEqual(report["commands"][0]["command"], "godot-pack-mod-doctor load-order base.json patch.json --format json")
            self.assertEqual(report["metadata"]["tool_version"], "0.1.4")
            self.assertEqual(report["metadata"]["risk"], "attention (10)")
            self.assertIn("Reproduce", html)
            self.assertIn("godot-pack-mod-doctor load-order base.json patch.json --format json", html)
            self.assertIn("Tool version", html)
            self.assertIn("0.1.4", html)
            self.assertIn("Risk", html)
            self.assertIn("attention (10)", html)


if __name__ == "__main__":
    unittest.main()
