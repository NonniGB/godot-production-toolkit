from __future__ import annotations

from contextlib import redirect_stdout
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
            self.assertEqual(report["tool_version"], "0.1.1")
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


if __name__ == "__main__":
    unittest.main()
