import json
import unittest

from gdscript_api_coverage.models import ApiItem, ThresholdFinding
from gdscript_api_coverage.reporting import render_json_report, render_markdown_index, render_text_report


class ReportingTests(unittest.TestCase):
    def test_markdown_index_contains_api_rows(self) -> None:
        items = [
            ApiItem(path="scripts/player.gd", line=3, kind="class", name="Player", documented=True),
            ApiItem(path="scripts/player.gd", line=9, kind="public_func", name="move", documented=False),
        ]

        markdown = render_markdown_index(items, title="API Index")

        self.assertIn("# API Index", markdown)
        self.assertIn("| class | Player | scripts/player.gd:3 | yes |", markdown)
        self.assertIn("| public_func | move | scripts/player.gd:9 | no |", markdown)

    def test_markdown_index_escapes_table_cells(self) -> None:
        item = ApiItem(path="scripts/player|debug.gd", line=3, kind="class", name="Player|Debug", documented=True)

        markdown = render_markdown_index([item], title="API Index")

        self.assertIn("scripts/player\\|debug.gd:3", markdown)
        self.assertIn("Player\\|Debug", markdown)

    def test_json_report_contains_summary_and_items(self) -> None:
        item = ApiItem(path="scripts/player.gd", line=3, kind="class", name="Player", documented=True)

        report = json.loads(render_json_report([item], []))

        self.assertEqual(report["metadata"]["schema_version"], "1.1")
        self.assertEqual(report["metadata"]["tool_version"], "0.1.3")
        self.assertEqual(report["summary"]["all"]["coverage"], 100.0)
        self.assertEqual(report["items"][0]["name"], "Player")

    def test_json_report_includes_rule_help_for_threshold_failures(self) -> None:
        finding = ThresholdFinding(
            kind="public_func",
            severity="error",
            message="public_func comment coverage is 50.00% but 80.00% is required.",
            actual=50.0,
            expected=80.0,
        )

        report = json.loads(render_json_report([], [finding]))

        self.assertEqual(report["rules"]["public_func_comment_coverage_below_threshold"]["title"], "Public functions coverage below threshold")
        self.assertEqual(report["findings"][0]["rule_id"], "public_func_comment_coverage_below_threshold")
        self.assertIn("public function documentation", report["findings"][0]["explanation"])

    def test_text_report_includes_plain_language_rule_help(self) -> None:
        finding = ThresholdFinding(
            kind="signal",
            severity="error",
            message="signal comment coverage is 0.00% but 100.00% is required.",
            actual=0.0,
            expected=100.0,
        )

        report = render_text_report([], [finding])

        self.assertIn("[ERROR] Signals coverage below threshold:", report)
        self.assertIn("Why it matters:", report)


if __name__ == "__main__":
    unittest.main()
