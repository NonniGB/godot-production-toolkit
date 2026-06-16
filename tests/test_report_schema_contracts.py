import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "docs" / "report-schemas"
SAMPLE_REPORTS = [
    ROOT / "docs" / "assets" / "sample-reports" / "assets.json",
    ROOT / "docs" / "assets" / "sample-reports" / "export.json",
    ROOT / "docs" / "assets" / "sample-reports" / "input-map.json",
    ROOT / "docs" / "assets" / "sample-reports" / "mobile-perf.json",
]


class ReportSchemaContractTests(unittest.TestCase):
    def test_report_schema_files_are_valid_json(self) -> None:
        for path in sorted(SCHEMA_DIR.glob("*.schema.json")):
            with self.subTest(path=path.name):
                schema = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual("https://json-schema.org/draft/2020-12/schema", schema["$schema"])
                self.assertIn("title", schema)
                self.assertIn("type", schema)

    def test_sample_reports_match_top_level_diagnostic_contract(self) -> None:
        for path in SAMPLE_REPORTS:
            with self.subTest(path=path.name):
                report = json.loads(path.read_text(encoding="utf-8"))
                self.assertIsInstance(report.get("tool"), str)
                self.assertTrue(report["tool"])
                self.assertIsInstance(report.get("summary"), dict)
                self.assertTrue(report["summary"])

                rows = report.get("findings", report.get("issues", []))
                self.assertIsInstance(rows, list)
                for row in rows:
                    self.assertIn(row.get("severity"), {"error", "warning", "info"})
                    self.assertIsInstance(row.get("message"), str)
                    self.assertTrue(row["message"])

    def test_report_schema_docs_explain_compatibility_policy(self) -> None:
        text = (SCHEMA_DIR / "README.md").read_text(encoding="utf-8")

        for phrase in (
            "stable top-level fields",
            "new fields may be added",
            "schema version bump",
            "tolerate unknown fields",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
