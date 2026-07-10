import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator
from referencing import Registry, Resource


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "docs" / "report-schemas"


def _validator() -> Draft202012Validator:
    report_schema = json.loads((SCHEMA_DIR / "tool-diagnostic-report-v1.schema.json").read_text(encoding="utf-8"))
    finding_schema = json.loads((SCHEMA_DIR / "finding-v1.schema.json").read_text(encoding="utf-8"))
    registry = Registry().with_resource(finding_schema["$id"], Resource.from_contents(finding_schema))
    Draft202012Validator.check_schema(report_schema)
    return Draft202012Validator(report_schema, registry=registry)


def _sample_reports() -> list[Path]:
    reports: list[Path] = []
    for path in sorted((ROOT / "docs" / "assets" / "sample-reports").glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict) and isinstance(data.get("summary"), dict) and (
            isinstance(data.get("tool"), str)
            or isinstance(data.get("metadata", {}).get("report_kind"), str)
        ):
            reports.append(path)
    return reports


class ReportSchemaContractTests(unittest.TestCase):
    def test_report_schema_files_are_valid_json(self) -> None:
        for path in sorted(SCHEMA_DIR.glob("*.schema.json")):
            with self.subTest(path=path.name):
                schema = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual("https://json-schema.org/draft/2020-12/schema", schema["$schema"])
                self.assertIn("title", schema)
                self.assertIn("type", schema)

    def test_sample_reports_match_top_level_diagnostic_contract(self) -> None:
        validator = _validator()
        reports = _sample_reports()
        self.assertTrue(reports)
        for path in reports:
            with self.subTest(path=path.name):
                report = json.loads(path.read_text(encoding="utf-8"))
                validator.validate(report)

    def test_invalid_summary_counts_are_rejected(self) -> None:
        validator = _validator()

        errors = list(validator.iter_errors({"tool": "demo", "summary": {"errors": None}}))

        self.assertTrue(errors)

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
