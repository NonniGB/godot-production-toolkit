import unittest

from godot_export_doctor.matrix import diff_report, render_matrix_report
from godot_export_doctor.models import ExportPreset


class MatrixDiffTests(unittest.TestCase):
    def test_diff_reports_renamed_preset_without_added_removed_noise(self) -> None:
        baseline = [
            ExportPreset(
                index=0,
                name="Web Release",
                platform="Web",
                runnable=False,
                export_filter="all_resources",
                export_path="build/web/index.html",
                options={"variant/export_type": 1},
            )
        ]
        current = [
            ExportPreset(
                index=0,
                name="Web Production",
                platform="Web",
                runnable=False,
                export_filter="all_resources",
                export_path="build/web/index.html",
                options={"variant/export_type": 1},
            )
        ]

        report = diff_report(baseline, current)

        self.assertEqual(report["diff"]["added"], [])
        self.assertEqual(report["diff"]["removed"], [])
        self.assertEqual(report["diff"]["changed"], [])
        self.assertEqual(report["diff"]["renamed"], [{"from": "Web Release", "to": "Web Production"}])
        self.assertEqual(report["summary"]["renamed"], 1)
        self.assertEqual(report["findings"][0]["rule_id"], "export_preset_renamed")
        self.assertEqual(report["findings"][0]["title"], "Export preset renamed")

        markdown = render_matrix_report(report, "markdown")
        text = render_matrix_report(report, "text")

        self.assertIn("Web Release -> Web Production", markdown)
        self.assertIn("Renamed: 1", text)


if __name__ == "__main__":
    unittest.main()
