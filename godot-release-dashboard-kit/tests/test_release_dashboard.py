from __future__ import annotations

from contextlib import redirect_stderr
import io
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
            self.assertEqual(data["tool_version"], "0.1.15")
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

    def test_html_dashboard_includes_status_and_workflow_filters(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reports = root / "reports"
            reports.mkdir()
            (reports / "export.json").write_text(
                json.dumps({"tool": "godot-export-preset-doctor", "summary": {"errors": 1, "warnings": 0}}),
                encoding="utf-8",
            )
            (reports / "scenario.json").write_text(
                json.dumps({"tool": "godot-scenario-report-kit", "summary": {"errors": 0, "warnings": 1}}),
                encoding="utf-8",
            )
            output = root / "dashboard.html"

            exit_code = main(["build", str(reports), "--output", str(output)])

            html = output.read_text(encoding="utf-8")
            self.assertEqual(exit_code, 0)
            self.assertIn('data-filter-status="blocked"', html)
            self.assertIn('data-filter-workflow="export"', html)
            self.assertIn('data-filter-workflow="runtime"', html)
            self.assertIn('data-status="blocked"', html)
            self.assertIn('data-workflow="runtime"', html)
            self.assertIn("showAllReports()", html)
            self.assertIn('href="#reports"', html)
            self.assertIn('id="reports"', html)
            self.assertIn('id="report-sections"', html)
            self.assertIn('aria-controls="report-sections"', html)
            self.assertIn('id="filter-status"', html)
            self.assertIn('aria-live="polite"', html)
            self.assertIn("<noscript>", html)
            self.assertIn("@media print", html)
            self.assertIn("focus-visible", html)
            self.assertIn('tabindex="0"', html)
            self.assertIn('aria-label="godot-scenario-report-kit report, attention, Runtime evidence"', html)

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
                            "visual_summary": {
                                "kind": "visual_smoke_report",
                                "relative_path": "../visual-smoke.json",
                                "captures": 2,
                                "comparisons": 2,
                                "changed": 1,
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
            self.assertEqual(dashboard["summary"]["visual_smoke_reports"], 1)
            self.assertEqual(dashboard["summary"]["visual_smoke_captures"], 2)
            self.assertEqual(dashboard["summary"]["visual_smoke_comparisons"], 2)
            self.assertEqual(dashboard["summary"]["visual_smoke_changed"], 1)
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
            self.assertEqual(scenario_bundle["visual_summary"]["changed"], 1)
            self.assertIn("Scenario Bundle Evidence", html)
            self.assertIn("Scenarios: 1 passed / 2 total", html)
            self.assertIn("Telemetry samples: 18", html)
            self.assertIn("Telemetry spikes: 2", html)
            self.assertIn("Telemetry: 18 samples", html)
            self.assertIn("frame p95 21.50 ms", html)
            self.assertIn("Visual smoke: 2 capture(s)", html)
            self.assertIn("../visual-smoke.json", html)
            self.assertIn("../runtime-timeline.html", html)
            self.assertIn("../run.log", html)
            self.assertIn("screenshots/menu.png", html)
            self.assertIn("Missing evidence: 1", html)

    def test_visual_smoke_reports_show_linked_screenshot_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reports = root / "reports"
            reports.mkdir()
            (reports / "visual-smoke.json").write_text(
                json.dumps(
                    {
                        "tool": "godot-visual-smoke-test-kit",
                        "kind": "visual_smoke_report",
                        "summary": {
                            "captures": 2,
                            "comparisons": 2,
                            "changed": 1,
                            "warnings": 1,
                            "errors": 0,
                        },
                        "screenshots": [
                            {"path": "screenshots/menu.png"},
                            {"path": "screenshots/trade-flow.png"},
                        ],
                        "findings": [
                            {
                                "severity": "warning",
                                "rule_id": "pixel_delta",
                                "message": "trade_flow changed beyond the configured visual threshold.",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            (reports / "compare.json").write_text(
                json.dumps(
                    {
                        "metadata": {"report_kind": "visual_smoke_compare"},
                        "summary": {"warnings": 1, "errors": 0},
                        "baseline": "baselines/menu.png",
                        "current": "current/menu.png",
                        "diff": "diffs/menu.png",
                        "changed_pixels": 4,
                        "total_pixels": 100,
                        "changed_percent": 4.0,
                    }
                ),
                encoding="utf-8",
            )
            output = root / "dashboard.html"

            dashboard = build_dashboard(reports)
            exit_code = main(["build", str(reports), "--output", str(output)])

            html = output.read_text(encoding="utf-8")
            reports_by_key = {report["report_key"]: report for report in dashboard["reports"]}
            self.assertEqual(exit_code, 0)
            self.assertEqual(dashboard["summary"]["visual_smoke_reports"], 2)
            self.assertEqual(dashboard["summary"]["visual_smoke_captures"], 2)
            self.assertEqual(dashboard["summary"]["visual_smoke_comparisons"], 2)
            self.assertEqual(dashboard["summary"]["visual_smoke_changed"], 2)
            self.assertEqual(reports_by_key["visual-smoke.json"]["visual_smoke"]["captures"], 2)
            self.assertEqual(reports_by_key["compare.json"]["visual_smoke"]["changed_pixels"], 4)
            self.assertIn("Visual Smoke Evidence", html)
            self.assertIn("Visual smoke reports: 2", html)
            self.assertIn("Visual captures: 2", html)
            self.assertIn("Visual changes: 2", html)
            self.assertIn("screenshots/menu.png", html)
            self.assertIn("diffs/menu.png", html)
            self.assertIn("Changed pixels: 4/100 (4.00%)", html)
            self.assertIn("pixel_delta", html)

    def test_scenario_flake_reports_show_retry_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reports = root / "reports"
            reports.mkdir()
            flake_report = reports / "scenario-flakes.json"
            flake_report.write_text(
                json.dumps(
                    {
                        "tool": "godot-scenario-report-kit",
                        "kind": "flake_compare",
                        "summary": {
                            "scenarios": 2,
                            "passed": 1,
                            "failed": 0,
                            "warnings": 2,
                            "errors": 0,
                            "flaky": 1,
                            "retried": 1,
                        },
                        "flake_groups": [
                            {
                                "scenario": "menu_startup",
                                "statuses": ["passed", "failed"],
                                "observations": [{"status": "passed"}, {"status": "failed"}],
                            }
                        ],
                        "retry_groups": [
                            {
                                "scenario": "trade_flow",
                                "run": "reports/retry-run",
                                "attempts": 2,
                                "statuses": ["failed", "passed"],
                                "final_status": "passed",
                                "observations": [{"status": "failed"}, {"status": "passed"}],
                            }
                        ],
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
            self.assertEqual(dashboard["summary"]["scenario_flake_reports"], 1)
            self.assertEqual(dashboard["summary"]["scenario_flaky"], 1)
            self.assertEqual(dashboard["summary"]["scenario_retried"], 1)
            self.assertEqual(report["status"], "attention")
            self.assertEqual(report["scenario_flakes"]["flaky"], 1)
            self.assertEqual(report["scenario_flakes"]["retried"], 1)
            self.assertIn("Scenario Flake and Retry Evidence", html)
            self.assertIn("Flaky scenarios: 1", html)
            self.assertIn("Retried scenarios: 1", html)
            self.assertIn("menu_startup", html)
            self.assertIn("trade_flow", html)
            self.assertIn("reports/retry-run", html)
            self.assertIn("Final status", html)

    def test_export_artifact_reports_show_file_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reports = root / "reports"
            reports.mkdir()
            export_report = reports / "exported-folder.json"
            export_report.write_text(
                json.dumps(
                    {
                        "tool": "godot-export-preset-doctor",
                        "kind": "exported_folder_inspection",
                        "summary": {
                            "files": 3,
                            "total_bytes": 4200,
                            "hashed_files": 2,
                            "errors": 0,
                            "warnings": 2,
                        },
                        "extensions": {".pck": 1, ".png": 1, ".keystore": 1},
                        "file_manifest": [
                            {
                                "path": "build/game.pck",
                                "extension": ".pck",
                                "size_bytes": 4096,
                                "sha256": "a" * 64,
                            },
                            {
                                "path": "build/icon.png",
                                "extension": ".png",
                                "size_bytes": 100,
                            },
                            {
                                "path": "build/release.keystore",
                                "extension": ".keystore",
                                "size_bytes": 4,
                                "sha256": "b" * 64,
                            },
                        ],
                        "findings": [
                            {
                                "rule_id": "exported_folder_dev_file",
                                "severity": "warning",
                                "message": "Exported folder contains development-looking file 'debug.log'.",
                            },
                            {
                                "rule_id": "exported_folder_private_file",
                                "severity": "warning",
                                "message": "Exported folder contains private file 'release.keystore'.",
                            },
                        ],
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
            self.assertEqual(dashboard["summary"]["export_artifact_reports"], 1)
            self.assertEqual(dashboard["summary"]["export_artifact_files"], 3)
            self.assertEqual(dashboard["summary"]["export_artifact_private_findings"], 1)
            self.assertEqual(dashboard["summary"]["export_artifact_dev_findings"], 1)
            self.assertEqual(report["export_artifacts"]["files"], 3)
            self.assertEqual(report["export_artifacts"]["hashed_files"], 2)
            self.assertEqual(report["export_artifacts"]["extensions"][".pck"], 1)
            self.assertIn("Export Artifact Evidence", html)
            self.assertIn("Files inspected: 3", html)
            self.assertIn("Files with SHA-256: 2", html)
            self.assertIn("Private/signing findings: 1", html)
            self.assertIn("Development file findings: 1", html)
            self.assertIn(".keystore", html)
            self.assertIn("build/release.keystore", html)

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

    def test_json_reports_surface_typed_highlights(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reports = root / "reports"
            reports.mkdir()
            (reports / "runtime.json").write_text(
                json.dumps(
                    {
                        "tool": "godot-runtime-telemetry-lab",
                        "kind": "runtime_telemetry_timeline",
                        "summary": {
                            "errors": 0,
                            "warnings": 1,
                            "samples": 18,
                            "scenarios": ["menu", "trade"],
                            "spikes": 2,
                            "frame_budget_ms": 16.67,
                            "frame_ms": {"p95": 21.5, "max": 33.1},
                            "memory_mb": {"max": 256.0},
                        },
                    }
                ),
                encoding="utf-8",
            )
            (reports / "pack.json").write_text(
                json.dumps(
                    {
                        "tool": "godot-pack-mod-doctor",
                        "kind": "pack_load_order",
                        "summary": {
                            "errors": 0,
                            "warnings": 1,
                            "packs": 2,
                            "files": 3,
                            "dependencies": 1,
                            "content_ids": 2,
                            "risk_score": 10,
                            "risk_level": "attention",
                        },
                        "packs": [
                            {"id": "base_pack"},
                            {"id": "patch_pack"},
                        ],
                    }
                ),
                encoding="utf-8",
            )

            dashboard = build_dashboard(reports)
            output = root / "dashboard.html"
            exit_code = main(["build", str(reports), "--output", str(output)])

            html = output.read_text(encoding="utf-8")
            self.assertEqual(exit_code, 0)
            by_tool = {report["tool"]: report for report in dashboard["reports"]}
            runtime_highlights = {
                item["label"]: item["value"]
                for item in by_tool["godot-runtime-telemetry-lab"]["highlights"]
            }
            pack_highlights = {
                item["label"]: item["value"]
                for item in by_tool["godot-pack-mod-doctor"]["highlights"]
            }
            self.assertEqual(runtime_highlights["Samples"], "18")
            self.assertEqual(runtime_highlights["Scenarios"], "2")
            self.assertEqual(runtime_highlights["Frame p95"], "21.50 ms")
            self.assertEqual(runtime_highlights["Memory max"], "256.0 MB")
            self.assertEqual(pack_highlights["Packs"], "2")
            self.assertEqual(pack_highlights["Risk"], "attention")
            self.assertEqual(pack_highlights["Pack order"], "base_pack -> patch_pack")
            self.assertIn("Highlights", html)
            self.assertIn("Frame p95", html)
            self.assertIn("21.50 ms", html)
            self.assertIn("Pack order", html)
            self.assertIn("base_pack -&gt; patch_pack", html)

    def test_builds_trend_cards_from_previous_report_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            previous = root / "previous"
            current = root / "current"
            previous.mkdir()
            current.mkdir()
            (previous / "export.json").write_text(
                json.dumps({"tool": "godot-export-doctor", "summary": {"errors": 1, "warnings": 2}}),
                encoding="utf-8",
            )
            (current / "export.json").write_text(
                json.dumps({"tool": "godot-export-doctor", "summary": {"errors": 0, "warnings": 1}}),
                encoding="utf-8",
            )
            (current / "new-check.json").write_text(
                json.dumps({"tool": "godot-mobile-ui-doctor", "summary": {"errors": 0, "warnings": 1}}),
                encoding="utf-8",
            )
            json_output = root / "dashboard.json"
            html_output = root / "dashboard.html"

            json_exit = main(
                [
                    "build",
                    str(current),
                    "--previous-reports-dir",
                    str(previous),
                    "--format",
                    "json",
                    "--output",
                    str(json_output),
                ]
            )
            html_exit = main(["build", str(current), "--baseline", str(previous), "--output", str(html_output)])

            data = json.loads(json_output.read_text(encoding="utf-8"))
            html = html_output.read_text(encoding="utf-8")
            self.assertEqual(json_exit, 0)
            self.assertEqual(html_exit, 0)
            self.assertTrue(data["trends"]["enabled"])
            self.assertEqual(data["previous_summary"]["blocked"], 1)
            self.assertEqual(data["previous_summary"]["errors"], 1)
            self.assertEqual(data["summary"]["trend_changes"], 2)
            self.assertEqual(data["summary"]["trend_improvements"], 1)
            self.assertEqual(data["summary"]["trend_regressions"], 1)
            status_counts = data["trends"]["status_counts"]
            self.assertEqual(status_counts[0]["label"], "Previous")
            self.assertEqual(status_counts[0]["blocked"], 1)
            self.assertEqual(status_counts[1]["label"], "Current")
            self.assertEqual(status_counts[1]["attention"], 2)
            self.assertEqual(data["trends"]["status_deltas"]["blocked"], -1)
            self.assertEqual(data["trends"]["status_deltas"]["attention"], 2)
            changes = {item["report_key"]: item for item in data["trends"]["changes"]}
            self.assertEqual(changes["export.json"]["direction"], "improvement")
            self.assertEqual(changes["export.json"]["error_delta"], -1)
            self.assertEqual(changes["new-check.json"]["change"], "added")
            self.assertIn("Changes Since Previous Reports", html)
            self.assertIn("Readiness Trend", html)
            self.assertIn('data-trend-status="blocked"', html)
            self.assertIn("Changed reports: 2", html)
            self.assertIn("improvement", html)
            self.assertIn("regression", html)
            self.assertNotIn(str(root), html)

    def test_build_accepts_dashboard_description_and_project_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reports = root / "reports"
            reports.mkdir()
            (reports / "notes.md").write_text("# Ready", encoding="utf-8")
            json_output = root / "dashboard.json"
            html_output = root / "dashboard.html"

            json_exit = main(
                [
                    "build",
                    str(reports),
                    "--title",
                    "Release Candidate Evidence",
                    "--description",
                    "Android export and runtime checks",
                    "--project",
                    "Demo Game",
                    "--format",
                    "json",
                    "--output",
                    str(json_output),
                ]
            )
            html_exit = main(
                [
                    "build",
                    str(reports),
                    "--title",
                    "Release Candidate Evidence",
                    "--description",
                    "Android export and runtime checks",
                    "--project",
                    "Demo Game",
                    "--output",
                    str(html_output),
                ]
            )

            data = json.loads(json_output.read_text(encoding="utf-8"))
            html = html_output.read_text(encoding="utf-8")
            self.assertEqual(json_exit, 0)
            self.assertEqual(html_exit, 0)
            self.assertEqual(data["title"], "Release Candidate Evidence")
            self.assertEqual(data["description"], "Android export and runtime checks")
            self.assertEqual(data["project"], "Demo Game")
            self.assertIn("Release Candidate Evidence", html)
            self.assertIn("Android export and runtime checks", html)
            self.assertIn("Demo Game", html)

    def test_empty_report_folder_warns_with_actionable_guidance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reports = root / "reports"
            reports.mkdir()
            output = root / "dashboard.json"
            stderr = io.StringIO()

            with redirect_stderr(stderr):
                exit_code = main(["build", str(reports), "--format", "json", "--output", str(output)])

            data = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(exit_code, 0)
            self.assertEqual(data["summary"]["reports"], 0)
            self.assertIn("No supported reports or images found", stderr.getvalue())
            self.assertIn("--require-reports", stderr.getvalue())

    def test_require_reports_fails_for_missing_or_empty_input(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            missing = root / "missing"
            output = root / "dashboard.html"
            stderr = io.StringIO()

            with redirect_stderr(stderr):
                exit_code = main(["build", str(missing), "--require-reports", "--output", str(output)])

            self.assertEqual(exit_code, 1)
            self.assertFalse(output.exists())
            self.assertIn("No supported reports or images found", stderr.getvalue())
            self.assertIn("godot-release-dashboard build", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
