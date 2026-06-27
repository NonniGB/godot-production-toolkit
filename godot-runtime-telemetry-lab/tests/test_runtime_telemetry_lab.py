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
            self.assertEqual(report["tool_version"], "0.1.4")
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

    def test_compare_reports_memory_regression(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            baseline = root / "baseline.json"
            current = root / "current.json"
            baseline.write_text(json.dumps([{"frame_ms": 12, "memory_mb": 200}]), encoding="utf-8")
            current.write_text(json.dumps([{"frame_ms": 12, "memory_mb": 280}]), encoding="utf-8")
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["compare", str(baseline), str(current), "--format", "json", "--fail-on", "none"])

            report = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            finding = report["findings"][0]
            self.assertEqual(finding["rule_id"], "memory_max_regression")
            self.assertEqual(report["summary"]["memory_delta_mb"], 80.0)

    def test_timeline_reports_spikes_and_html(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "telemetry.json"
            path.write_text(
                json.dumps(
                    {
                        "samples": [
                            {"scenario": "flight", "phase": "launch", "time_s": 0, "frame_ms": 12, "memory_mb": 220},
                            {"scenario": "flight", "phase": "combat", "time_s": 1, "frame_ms": 34, "memory_mb": 260},
                        ]
                    }
                ),
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["timeline", str(path), "--frame-budget-ms", "16", "--format", "html", "--fail-on", "none"])

            rendered = stdout.getvalue()
            self.assertEqual(exit_code, 0)
            self.assertIn("<svg", rendered)
            self.assertIn("frame_over_budget", rendered)

    def test_budget_init_can_drive_timeline_budget_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            budget_path = root / "budget.json"
            telemetry_path = root / "telemetry.json"
            telemetry_path.write_text(json.dumps([{"frame_ms": 35, "memory_mb": 700}]), encoding="utf-8")

            exit_code = main(["budget", "init", "--profile", "android-low", "--output", str(budget_path)])
            self.assertEqual(exit_code, 0)
            budget = json.loads(budget_path.read_text(encoding="utf-8"))
            self.assertEqual(budget["frame_budget_ms"], 33.33)

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["timeline", str(telemetry_path), "--budget-file", str(budget_path), "--format", "json", "--fail-on", "none"])

            report = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(report["summary"]["frame_budget_ms"], 33.33)
            self.assertEqual(report["spikes"][0]["rule_id"], "frame_over_budget")

    def test_adapt_normalizes_godot_monitor_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "godot-monitor.csv"
            path.write_text(
                "scenario,fps,Performance.MEMORY_STATIC,Performance.OBJECT_NODE_COUNT,Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME\n"
                "menu,50,104857600,42,8\n",
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["adapt", str(path), "--format", "json"])

            report = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(report["kind"], "runtime_telemetry_adapter")
            self.assertEqual(report["samples"][0]["scenario"], "menu")
            self.assertAlmostEqual(report["samples"][0]["frame_ms"], 20.0)
            self.assertAlmostEqual(report["samples"][0]["memory_mb"], 100.0)
            self.assertEqual(report["samples"][0]["nodes"], 42)
            self.assertEqual(report["samples"][0]["draw_calls"], 8)

    def test_adapt_converts_godot_performance_seconds_and_memory_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "godot-performance.csv"
            path.write_text(
                "scenario,Performance.TIME_PROCESS,Performance.TIME_PHYSICS_PROCESS,"
                "Performance.RENDER_VIDEO_MEM_USED,Performance.OBJECT_NODE_COUNT,"
                "Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME\n"
                "flight,0.018,0.004,209715200,80,12\n",
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["adapt", str(path), "--format", "json"])

            report = json.loads(stdout.getvalue())
            sample = report["samples"][0]
            self.assertEqual(exit_code, 0)
            self.assertEqual(sample["scenario"], "flight")
            self.assertAlmostEqual(sample["frame_ms"], 18.0)
            self.assertAlmostEqual(sample["physics_ms"], 4.0)
            self.assertAlmostEqual(sample["memory_mb"], 200.0)
            self.assertEqual(sample["nodes"], 80)
            self.assertEqual(sample["draw_calls"], 12)


if __name__ == "__main__":
    unittest.main()
