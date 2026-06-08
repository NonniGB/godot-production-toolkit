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
        self.assertIn("godot-save-guard 0.1.0", stdout.getvalue())

    def test_markdown_report_lists_fixture_findings(self) -> None:
        report = render_markdown_report(
            [FixtureResult(Path("saves/v1/save.json"), [Finding("missing_version_field", "error", "$", "Missing version.")])]
        )

        self.assertIn("# Save Compatibility Report", report)
        self.assertIn("| error | missing_version_field | saves/v1/save.json |", report)

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
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["summary"]["errors"], 1)


if __name__ == "__main__":
    unittest.main()
