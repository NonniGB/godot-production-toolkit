import json
import unittest

from godot_export_doctor.models import ExportPreset, Finding
from godot_export_doctor.reporting import render_json_report, render_sarif_report, render_text_report


class ReportingTests(unittest.TestCase):
    def test_json_report_is_machine_readable(self) -> None:
        preset = ExportPreset(index=0, name="Android", platform="Android", export_path="")
        finding = Finding(
            rule_id="missing_export_path",
            severity="error",
            preset_index=0,
            preset_name="Android",
            message="Export path is missing.",
        )

        report = json.loads(render_json_report([preset], [finding]))

        self.assertEqual(report["metadata"]["schema_version"], "1.1")
        self.assertEqual(report["metadata"]["tool_version"], "0.1.13")
        self.assertEqual(report["summary"]["presets"], 1)
        self.assertEqual(report["summary"]["errors"], 1)
        self.assertEqual(report["rules"]["missing_export_path"]["title"], "Missing export path")
        self.assertEqual(report["findings"][0]["rule_id"], "missing_export_path")
        self.assertEqual(report["findings"][0]["title"], "Missing export path")
        self.assertIn("target path", report["findings"][0]["explanation"])

    def test_sarif_report_contains_rules_and_results(self) -> None:
        finding = Finding(
            rule_id="missing_export_path",
            severity="error",
            preset_index=0,
            preset_name="Android",
            message="Export path is missing.",
        )

        report = json.loads(render_sarif_report([finding]))

        self.assertEqual(report["version"], "2.1.0")
        self.assertEqual(report["runs"][0]["results"][0]["ruleId"], "missing_export_path")
        self.assertEqual(report["runs"][0]["tool"]["driver"]["rules"][0]["name"], "Missing export path")

    def test_text_report_includes_clean_summary_when_no_findings(self) -> None:
        preset = ExportPreset(index=0, name="Web", platform="Web", export_path="build/web/index.html")

        report = render_text_report([preset], [])

        self.assertIn("1 export preset", report)
        self.assertIn("No findings", report)


if __name__ == "__main__":
    unittest.main()
