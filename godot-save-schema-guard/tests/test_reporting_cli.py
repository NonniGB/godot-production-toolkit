from contextlib import redirect_stdout
from io import StringIO
import json
import tempfile
import unittest
from pathlib import Path

from godot_save_guard.cli import main
from godot_save_guard.models import Finding, FixtureResult
from godot_save_guard.reporting import render_markdown_report


class ReportingCliTests(unittest.TestCase):
    def test_cli_prints_version(self) -> None:
        stdout = StringIO()

        with self.assertRaises(SystemExit) as raised:
            with redirect_stdout(stdout):
                main(["--version"])

        self.assertEqual(raised.exception.code, 0)
        self.assertIn("godot-save-guard 0.1.3", stdout.getvalue())

    def test_markdown_report_lists_fixture_findings(self) -> None:
        report = render_markdown_report(
            [FixtureResult(Path("saves/v1/save.json"), [Finding("missing_version_field", "error", "$", "Missing version.")])]
        )

        self.assertIn("# Save Compatibility Report", report)
        self.assertIn("| error | missing_version_field | saves/v1/save.json |", report)
        self.assertIn("top-level version", report)

    def test_markdown_report_escapes_table_cells(self) -> None:
        report = render_markdown_report(
            [
                FixtureResult(
                    Path("saves/v1/save|demo.json"),
                    [Finding("unexpected_property", "warning", "$.items|debug", "Field contains | pipe")],
                )
            ]
        )

        self.assertIn("save\\|demo.json", report)
        self.assertIn("$.items\\|debug", report)
        self.assertIn("Field contains \\| pipe", report)

    def test_cli_validate_writes_json_and_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = root / "save.json"
            schema = root / "schema.json"
            output = root / "report.json"
            fixture.write_text(json.dumps({"version": "1"}), encoding="utf-8")
            schema.write_text(
                json.dumps({"type": "object", "required": ["version"], "properties": {"version": {"type": "integer"}}}),
                encoding="utf-8",
            )

            exit_code = main(["validate", str(fixture), "--schema", str(schema), "--format", "json", "--output", str(output)])

            self.assertEqual(exit_code, 1)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(report["metadata"]["schema_version"], "1.1")
            self.assertEqual(report["metadata"]["tool_version"], "0.1.3")
            self.assertEqual(report["summary"]["errors"], 1)
            self.assertEqual(report["rules"]["numeric_type_drift"]["title"], "Numeric type drift")
            finding = report["fixtures"][0]["findings"][0]
            self.assertEqual(finding["title"], "Numeric type drift")
            self.assertIn("saved as text", finding["explanation"])

    def test_cli_validate_reports_empty_fixture_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixtures = root / "fixtures"
            fixtures.mkdir()
            schema = root / "schema.json"
            schema.write_text(json.dumps({"type": "object"}), encoding="utf-8")
            output = root / "report.json"

            exit_code = main(["validate", str(fixtures), "--schema", str(schema), "--format", "json", "--output", str(output)])

            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(exit_code, 1)
            self.assertIn("no_fixtures", {finding["rule_id"] for fixture in report["fixtures"] for finding in fixture["findings"]})

    def test_cli_migrate_chain_dry_run_reports_planned_steps(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = root / "save.json"
            chain = root / "chain.toml"
            output = root / "report.json"
            fixture.write_text(json.dumps({"version": 1}), encoding="utf-8")
            chain.write_text(
                "\n".join(
                    [
                        "[[steps]]",
                        'from = "1"',
                        'to = "2"',
                        'command = "migrate-v1-v2 {input} {output}"',
                        "",
                        "[[steps]]",
                        'from = "2"',
                        'to = "3"',
                        'command = "migrate-v2-v3 {input} {output}"',
                    ]
                ),
                encoding="utf-8",
            )

            exit_code = main(
                [
                    "migrate-chain",
                    str(fixture),
                    "--chain",
                    str(chain),
                    "--output-dir",
                    str(root / "migrated"),
                    "--dry-run",
                    "--format",
                    "json",
                    "--output",
                    str(output),
                ]
            )

            report = json.loads(output.read_text(encoding="utf-8"))
            findings = report["fixtures"][0]["findings"]
            self.assertEqual(exit_code, 0)
            self.assertEqual(findings[0]["rule_id"], "migration_chain_planned")
            self.assertIn("1->2, 2->3", findings[0]["message"])

    def test_cli_migration_graph_reports_missing_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            chain = root / "chain.toml"
            output = root / "graph.json"
            chain.write_text(
                "\n".join(
                    [
                        "[[steps]]",
                        'from = "1"',
                        'to = "2"',
                        'command = "migrate-v1-v2 {input} {output}"',
                        "",
                        "[[steps]]",
                        'from = "3"',
                        'to = "4"',
                        'command = "migrate-v3-v4 {input} {output}"',
                    ]
                ),
                encoding="utf-8",
            )

            exit_code = main(
                [
                    "migration-graph",
                    "--chain",
                    str(chain),
                    "--current",
                    "4",
                    "--supported",
                    "1",
                    "--supported",
                    "3",
                    "--format",
                    "json",
                    "--output",
                    str(output),
                ]
            )

            report = json.loads(output.read_text(encoding="utf-8"))
            findings = report["fixtures"][0]["findings"]
            self.assertEqual(exit_code, 1)
            self.assertEqual(findings[0]["rule_id"], "migration_path_missing")
            self.assertIn("version 1", findings[0]["message"])


if __name__ == "__main__":
    unittest.main()
