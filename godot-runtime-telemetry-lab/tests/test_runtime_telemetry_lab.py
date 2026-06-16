from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from godot_runtime_telemetry_lab.cli import main


class RuntimeTelemetryLabTests(unittest.TestCase):
    def test_summarize_reports_frame_budget_warning(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "telemetry.json"
            path.write_text(
                json.dumps({"samples": [{"scenario": "menu", "frame_ms": 12}, {"scenario": "menu", "frame_ms": 24}]}),
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["summarize", str(path), "--frame-budget-ms", "16", "--format", "json", "--fail-on", "none"])

            report = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(report["tool_version"], "0.1.0")
            self.assertEqual(report["summary"]["samples"], 2)
            self.assertEqual(report["findings"][0]["rule_id"], "frame_p95_over_budget")

    def test_compare_reports_regression(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            baseline = root / "baseline.json"
            current = root / "current.json"
            baseline.write_text(json.dumps([{"frame_ms": 10}, {"frame_ms": 12}]), encoding="utf-8")
            current.write_text(json.dumps([{"frame_ms": 20}, {"frame_ms": 24}]), encoding="utf-8")
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["compare", str(baseline), str(current), "--format", "json", "--fail-on", "none"])

            report = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            rules = {finding["rule_id"] for finding in report["findings"]}
            self.assertIn("frame_p95_regression", rules)


if __name__ == "__main__":
    unittest.main()
