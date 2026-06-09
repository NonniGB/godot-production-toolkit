from contextlib import redirect_stdout
from io import StringIO
import json
import tempfile
import unittest
from pathlib import Path

from gdscript_api_coverage.cli import main


class CliTests(unittest.TestCase):
    def test_cli_prints_version(self) -> None:
        stdout = StringIO()

        with self.assertRaises(SystemExit) as raised:
            with redirect_stdout(stdout):
                main(["--version"])

        self.assertEqual(raised.exception.code, 0)
        self.assertIn("gdscript-api-coverage 0.1.2", stdout.getvalue())

    def test_cli_writes_docs_and_returns_failure_for_threshold(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            scripts = project / "scripts"
            scripts.mkdir()
            (scripts / "player.gd").write_text(
                """
class_name Player

func move() -> void:
    pass
""",
                encoding="utf-8",
            )
            docs_path = project / "docs" / "API_INDEX.md"

            exit_code = main([str(project), "--min-all", "100", "--write-docs", str(docs_path)])

            self.assertEqual(exit_code, 1)
            self.assertIn("Player", docs_path.read_text(encoding="utf-8"))

    def test_cli_writes_json_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / "player.gd").write_text(
                """
## Player API.
class_name Player
""",
                encoding="utf-8",
            )
            output = project / "report.json"

            exit_code = main([str(project), "--format", "json", "--output", str(output)])

            self.assertEqual(exit_code, 0)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["summary"]["all"]["total"], 1)

    def test_cli_can_write_markdown_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / "player.gd").write_text("class_name Player\n", encoding="utf-8")
            output = project / "api.md"

            exit_code = main([str(project), "--format", "markdown", "--output", str(output)])

            self.assertEqual(exit_code, 0)
            markdown = output.read_text(encoding="utf-8")
            self.assertIn("# GDScript API Index", markdown)
            self.assertIn("Player", markdown)
            self.assertTrue(markdown.endswith("\n"))

    def test_cli_rejects_thresholds_outside_percent_range(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            cases = [
                ["--min-all", "-1"],
                ["--min-public-func", "101"],
            ]

            for extra_args in cases:
                with self.subTest(extra_args=extra_args):
                    with self.assertRaises(SystemExit) as raised:
                        main([str(project), *extra_args])

                    self.assertEqual(raised.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
