import json
import unittest

from gdscript_api_coverage.models import ApiItem
from gdscript_api_coverage.reporting import render_json_report, render_markdown_index


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

    def test_json_report_contains_summary_and_items(self) -> None:
        item = ApiItem(path="scripts/player.gd", line=3, kind="class", name="Player", documented=True)

        report = json.loads(render_json_report([item], []))

        self.assertEqual(report["summary"]["all"]["coverage"], 100.0)
        self.assertEqual(report["items"][0]["name"], "Player")


if __name__ == "__main__":
    unittest.main()
