from contextlib import redirect_stdout
from io import StringIO
import json
import tempfile
import unittest
from pathlib import Path

from godot_l10n_guard.cli import main
from godot_l10n_guard.models import Finding
from godot_l10n_guard.reporting import render_markdown_report


class ReportingCliTests(unittest.TestCase):
    def test_cli_prints_version(self) -> None:
        stdout = StringIO()

        with self.assertRaises(SystemExit) as raised:
            with redirect_stdout(stdout):
                main(["--version"])

        self.assertEqual(raised.exception.code, 0)
        self.assertIn("godot-l10n-guard 0.1.0", stdout.getvalue())

    def test_markdown_report_lists_findings(self) -> None:
        markdown = render_markdown_report(
            [],
            [Finding("empty_translation", "error", "MENU_EXIT", "Missing fr", "strings.csv", 3)],
        )

        self.assertIn("# Localization QA Report", markdown)
        self.assertIn("| error | empty_translation | MENU_EXIT |", markdown)

    def test_cli_writes_json_report_and_fails_on_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            csv_path = project / "strings.csv"
            csv_path.write_text("keys,en,fr\nMENU_START,Start,\n", encoding="utf-8")
            output = project / "report.json"

            exit_code = main(
                [str(project), "--csv", str(csv_path), "--require", "fr", "--format", "json", "--output", str(output)]
            )

            self.assertEqual(exit_code, 1)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(report["summary"]["errors"], 1)

    def test_cli_outputs_sarif_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            csv_path = project / "strings.csv"
            csv_path.write_text("keys,en,fr\nMENU_START,Start,\n", encoding="utf-8")
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(
                    [str(project), "--csv", str(csv_path), "--require", "fr", "--format", "sarif", "--fail-on", "none"]
                )

            sarif = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(sarif["version"], "2.1.0")
            driver = sarif["runs"][0]["tool"]["driver"]
            self.assertEqual(driver["name"], "godot-localization-qa-guard")
            self.assertTrue(driver["rules"])
            self.assertTrue(sarif["runs"][0]["results"])


if __name__ == "__main__":
    unittest.main()
