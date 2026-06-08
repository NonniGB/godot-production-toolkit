import unittest

from gdscript_api_coverage.coverage import build_summary, evaluate_thresholds
from gdscript_api_coverage.models import ApiItem


class CoverageTests(unittest.TestCase):
    def test_builds_summary_by_kind(self) -> None:
        items = [
            ApiItem(path="a.gd", line=1, kind="public_func", name="start", documented=True),
            ApiItem(path="a.gd", line=4, kind="public_func", name="stop", documented=False),
            ApiItem(path="a.gd", line=8, kind="signal", name="changed", documented=True),
        ]

        summary = build_summary(items)

        self.assertEqual(summary["all"]["total"], 3)
        self.assertEqual(summary["all"]["documented"], 2)
        self.assertAlmostEqual(summary["all"]["coverage"], 66.67)
        self.assertEqual(summary["public_func"]["total"], 2)

    def test_threshold_failure_reports_kind(self) -> None:
        items = [
            ApiItem(path="a.gd", line=1, kind="public_func", name="start", documented=True),
            ApiItem(path="a.gd", line=4, kind="public_func", name="stop", documented=False),
        ]

        findings = evaluate_thresholds(items, {"all": 80, "public_func": 75})

        self.assertEqual({finding.kind for finding in findings}, {"all", "public_func"})
        self.assertTrue(all(finding.severity == "error" for finding in findings))


if __name__ == "__main__":
    unittest.main()
