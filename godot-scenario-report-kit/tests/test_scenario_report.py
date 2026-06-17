from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from godot_scenario_report_kit.cli import main


class ScenarioReportTests(unittest.TestCase):
    def test_summarize_reports_failed_assertions_and_missing_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "trade.json").write_text(
                json.dumps(
                    {
                        "scenario": "trade_flow",
                        "status": "failed",
                        "duration_ms": 1200,
                        "assertions": [{"name": "trade completed", "status": "failed", "message": "No stock."}],
                        "artifacts": ["screenshots/trade.png"],
                    }
                ),
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["summarize", str(root), "--format", "json", "--fail-on", "none"])

            report = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(report["tool_version"], "0.1.5")
            self.assertEqual(report["schema_version"], "1.1")
            self.assertIn("scenario_failed", report["metadata"]["rules"])
            self.assertEqual(report["summary"]["scenarios"], 1)
            rules = {finding["rule_id"] for finding in report["findings"]}
            self.assertIn("scenario_failed", rules)
            self.assertIn("assertion_failed", rules)
            self.assertIn("missing_artifact", rules)
            self.assertTrue(all("rule_help" in finding for finding in report["findings"]))

    def test_compare_reports_new_failures_and_duration_regression(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            baseline = root / "baseline"
            current = root / "current"
            baseline.mkdir()
            current.mkdir()
            (baseline / "menu.json").write_text(
                json.dumps({"scenario": "menu", "status": "passed", "duration_ms": 100}),
                encoding="utf-8",
            )
            (current / "menu.json").write_text(
                json.dumps({"scenario": "menu", "status": "failed", "duration_ms": 300}),
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["compare", str(baseline), str(current), "--format", "json", "--fail-on", "none"])

            report = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            rules = {finding["rule_id"] for finding in report["findings"]}
            self.assertIn("new_scenario_failure", rules)
            self.assertIn("duration_regression", rules)

    def test_markdown_includes_rule_help(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "trade.json").write_text(
                json.dumps({"scenario": "trade_flow", "status": "failed"}),
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["summarize", str(root), "--format", "markdown", "--fail-on", "none"])

            self.assertEqual(exit_code, 0)
            markdown = stdout.getvalue()
            self.assertIn("| Severity | Rule | Scenario | Message | Help |", markdown)
            self.assertIn("Open the scenario source", markdown)

    def test_manifest_check_reports_coverage_and_missing_results(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = root / "scenario-manifest.json"
            results = root / "results"
            results.mkdir()
            manifest.write_text(
                json.dumps(
                    {
                        "coverage": {
                            "required_tags": ["smoke", "combat"],
                            "required_critical_flows": ["startup", "trade"],
                            "required_platforms": ["desktop", "android"],
                        },
                        "scenarios": [
                            {
                                "id": "menu_startup",
                                "owner": "ui",
                                "tags": ["smoke"],
                                "critical_flows": ["startup"],
                                "platforms": ["desktop"],
                                "expected_artifacts": ["screenshots/menu.png"],
                            },
                            {
                                "id": "trade_flow",
                                "owner": "",
                                "tags": [],
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )
            (results / "menu_startup.json").write_text(
                json.dumps({"scenario": "menu_startup", "status": "passed"}),
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "manifest",
                        "check",
                        str(manifest),
                        "--results",
                        str(results),
                        "--format",
                        "json",
                        "--fail-on",
                        "none",
                    ]
                )

            report = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            rules = {finding["rule_id"] for finding in report["findings"]}
            self.assertIn("manifest_result_missing", rules)
            self.assertIn("manifest_expected_artifact_missing", rules)
            self.assertIn("coverage_required_tag_missing", rules)
            self.assertEqual(report["coverage"]["missing_required_tags"], ["combat"])

    def test_flake_compare_reports_status_changes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_a = root / "run-a"
            run_b = root / "run-b"
            run_a.mkdir()
            run_b.mkdir()
            (run_a / "menu.json").write_text(
                json.dumps({"scenario": "menu_startup", "status": "passed"}),
                encoding="utf-8",
            )
            (run_b / "menu.json").write_text(
                json.dumps({"scenario": "menu_startup", "status": "failed"}),
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(
                    ["flake", "compare", str(run_a), str(run_b), "--format", "markdown", "--fail-on", "none"]
                )

            markdown = stdout.getvalue()
            self.assertEqual(exit_code, 0)
            self.assertIn("flaky_scenario", markdown)
            self.assertIn("Flaky Scenarios", markdown)

    def test_bundle_links_telemetry_visual_and_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            results = root / "results"
            results.mkdir()
            (results / "screenshots").mkdir()
            (results / "screenshots" / "menu.png").write_bytes(b"png")
            telemetry = root / "telemetry.json"
            visual = root / "visual.json"
            manifest = root / "scenario-manifest.json"
            telemetry.write_text(json.dumps({"samples": [{"frame_ms": 12}]}), encoding="utf-8")
            visual.write_text(json.dumps({"summary": {"warnings": 0}}), encoding="utf-8")
            manifest.write_text(
                json.dumps({"scenarios": [{"id": "menu", "owner": "ui", "tags": ["smoke"]}]}),
                encoding="utf-8",
            )
            (results / "menu.json").write_text(
                json.dumps(
                    {
                        "scenario": "menu",
                        "status": "passed",
                        "artifacts": ["screenshots/menu.png", "missing.log"],
                    }
                ),
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "bundle",
                        str(results),
                        "--manifest",
                        str(manifest),
                        "--telemetry",
                        str(telemetry),
                        "--visual",
                        str(visual),
                        "--format",
                        "json",
                        "--fail-on",
                        "none",
                    ]
                )

            report = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(report["kind"], "scenario_bundle")
            self.assertEqual(report["summary"]["linked_evidence"], 3)
            self.assertEqual(report["summary"]["artifacts"], 2)
            self.assertIn("telemetry", report["bundle"]["links"])
            self.assertIn("visual", report["bundle"]["links"])
            self.assertEqual(report["bundle"]["telemetry_summary"]["samples"], 1)
            self.assertEqual(report["bundle"]["telemetry_summary"]["frame_max_ms"], 12.0)
            self.assertIn("bundle_missing_artifact", {finding["rule_id"] for finding in report["findings"]})

    def test_bundle_summarizes_runtime_telemetry_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            results = root / "results"
            results.mkdir()
            telemetry = root / "runtime-summary.json"
            telemetry.write_text(
                json.dumps(
                    {
                        "tool": "godot-runtime-telemetry-lab",
                        "kind": "runtime_telemetry_timeline",
                        "summary": {
                            "samples": 3,
                            "scenarios": ["menu"],
                            "frame_ms": {"p95": 21.5, "max": 33.1},
                            "memory_mb": {"max": 256.0},
                            "spikes": 2,
                            "warnings": 1,
                            "errors": 0,
                        },
                        "samples": [{"frame_ms": 12}, {"frame_ms": 21.5}, {"frame_ms": 33.1}],
                        "findings": [{"severity": "warning", "rule_id": "frame_over_budget"}],
                    }
                ),
                encoding="utf-8",
            )
            (results / "menu.json").write_text(
                json.dumps({"scenario": "menu", "status": "passed"}),
                encoding="utf-8",
            )

            json_stdout = StringIO()
            with redirect_stdout(json_stdout):
                json_exit = main(
                    [
                        "bundle",
                        str(results),
                        "--telemetry",
                        str(telemetry),
                        "--format",
                        "json",
                        "--fail-on",
                        "none",
                    ]
                )

            markdown_stdout = StringIO()
            with redirect_stdout(markdown_stdout):
                markdown_exit = main(
                    [
                        "bundle",
                        str(results),
                        "--telemetry",
                        str(telemetry),
                        "--format",
                        "markdown",
                        "--fail-on",
                        "none",
                    ]
                )

            report = json.loads(json_stdout.getvalue())
            self.assertEqual(json_exit, 0)
            self.assertEqual(markdown_exit, 0)
            telemetry_summary = report["bundle"]["telemetry_summary"]
            self.assertEqual(report["summary"]["telemetry_samples"], 3)
            self.assertEqual(report["summary"]["telemetry_warnings"], 1)
            self.assertEqual(telemetry_summary["kind"], "runtime_telemetry_timeline")
            self.assertEqual(telemetry_summary["frame_p95_ms"], 21.5)
            self.assertEqual(telemetry_summary["frame_max_ms"], 33.1)
            self.assertEqual(telemetry_summary["memory_max_mb"], 256.0)
            self.assertEqual(telemetry_summary["spikes"], 2)
            self.assertIn("| Frame p95 ms | 21.50 |", markdown_stdout.getvalue())

    def test_bundle_summarizes_runtime_telemetry_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            results = root / "results"
            results.mkdir()
            telemetry = root / "runtime.md"
            telemetry.write_text(
                "\n".join(
                    [
                        "# Godot Runtime Telemetry Timeline",
                        "",
                        "| Metric | Value |",
                        "|---|---:|",
                        "| Samples | 5 |",
                        "| Frame p95 ms | 24.50 |",
                        "| Frame max ms | 35.00 |",
                        "| Spikes | 2 |",
                    ]
                ),
                encoding="utf-8",
            )
            (results / "menu.json").write_text(
                json.dumps({"scenario": "menu", "status": "passed"}),
                encoding="utf-8",
            )

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "bundle",
                        str(results),
                        "--telemetry",
                        str(telemetry),
                        "--format",
                        "json",
                        "--fail-on",
                        "none",
                    ]
                )

            report = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            telemetry_summary = report["bundle"]["telemetry_summary"]
            self.assertEqual(report["summary"]["telemetry_samples"], 5)
            self.assertEqual(report["summary"]["telemetry_spikes"], 2)
            self.assertEqual(telemetry_summary["kind"], "runtime_telemetry_markdown")
            self.assertEqual(telemetry_summary["frame_p95_ms"], 24.5)
            self.assertEqual(telemetry_summary["frame_max_ms"], 35.0)

    def test_bundle_enriches_unreadable_telemetry_finding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            results = root / "results"
            results.mkdir()
            telemetry = root / "runtime.json"
            telemetry.write_text("{broken", encoding="utf-8")
            (results / "menu.json").write_text(
                json.dumps({"scenario": "menu", "status": "passed"}),
                encoding="utf-8",
            )

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "bundle",
                        str(results),
                        "--telemetry",
                        str(telemetry),
                        "--format",
                        "json",
                        "--fail-on",
                        "none",
                    ]
                )

            report = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            finding = next(
                item for item in report["findings"] if item["rule_id"] == "bundle_telemetry_unreadable"
            )
            self.assertEqual(finding["rule_title"], "Telemetry summary could not be read")
            self.assertIn("Linked telemetry JSON", finding["message"])

    def test_bundle_accepts_custom_evidence_links(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            results = root / "results"
            results.mkdir()
            log = root / "run.log"
            junit = root / "junit.xml"
            captures = root / "captures"
            captures.mkdir()
            log.write_text("scenario run log", encoding="utf-8")
            junit.write_text("<testsuite />", encoding="utf-8")
            (results / "menu.json").write_text(
                json.dumps({"scenario": "menu", "status": "passed"}),
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "bundle",
                        str(results),
                        "--evidence",
                        f"log={log}",
                        "--evidence",
                        f"junit={junit}",
                        "--evidence",
                        f"captures={captures}",
                        "--evidence",
                        f"coverage={root / 'missing-coverage.json'}",
                        "--format",
                        "json",
                        "--fail-on",
                        "none",
                    ]
                )

            report = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(report["summary"]["linked_evidence"], 4)
            evidence = report["bundle"]["evidence_links"]
            self.assertEqual([item["kind"] for item in evidence], ["log", "junit", "captures", "coverage"])
            self.assertEqual(evidence[0]["size_bytes"], len("scenario run log"))
            self.assertTrue(evidence[2]["is_dir"])
            self.assertNotIn("size_bytes", evidence[2])
            self.assertFalse(evidence[3]["exists"])
            self.assertIn("bundle_link_missing", {finding["rule_id"] for finding in report["findings"]})

    def test_bundle_markdown_and_html_show_linked_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            results = root / "results"
            results.mkdir()
            (results / "menu.json").write_text(
                json.dumps({"scenario": "menu", "status": "passed", "artifacts": ["menu.png"]}),
                encoding="utf-8",
            )
            (results / "menu.png").write_bytes(b"png")
            log = root / "run.log"
            log.write_text("log", encoding="utf-8")

            markdown_stdout = StringIO()
            with redirect_stdout(markdown_stdout):
                markdown_exit = main(
                    [
                        "bundle",
                        str(results),
                        "--evidence",
                        f"run|log={log}",
                        "--format",
                        "markdown",
                        "--fail-on",
                        "none",
                    ]
                )

            html_stdout = StringIO()
            with redirect_stdout(html_stdout):
                html_exit = main(
                    [
                        "bundle",
                        str(results),
                        "--evidence",
                        f"run|log={log}",
                        "--format",
                        "html",
                        "--fail-on",
                        "none",
                    ]
                )

            self.assertEqual(markdown_exit, 0)
            self.assertEqual(html_exit, 0)
            self.assertIn("## Bundle Evidence", markdown_stdout.getvalue())
            self.assertIn("| run\\|log |", markdown_stdout.getvalue())
            self.assertIn("## Bundle Artifacts", markdown_stdout.getvalue())
            self.assertIn("<h2>Bundle Evidence</h2>", html_stdout.getvalue())
            self.assertIn("menu.png", html_stdout.getvalue())

    def test_bundle_rejects_invalid_custom_evidence_argument(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            results = root / "results"
            results.mkdir()
            (results / "menu.json").write_text(
                json.dumps({"scenario": "menu", "status": "passed"}),
                encoding="utf-8",
            )

            stderr = StringIO()
            with redirect_stderr(stderr), self.assertRaises(SystemExit) as raised:
                main(["bundle", str(results), "--evidence", "not-a-pair"])

            self.assertEqual(raised.exception.code, 2)
            self.assertIn("KIND=PATH", stderr.getvalue())

            with redirect_stderr(StringIO()), self.assertRaises(SystemExit) as empty_kind:
                main(["bundle", str(results), "--evidence", f"={root / 'run.log'}"])
            self.assertEqual(empty_kind.exception.code, 2)

            with redirect_stderr(StringIO()), self.assertRaises(SystemExit) as empty_path:
                main(["bundle", str(results), "--evidence", "log="])
            self.assertEqual(empty_path.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
