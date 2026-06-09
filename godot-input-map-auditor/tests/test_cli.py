from contextlib import redirect_stdout
from io import StringIO
import tempfile
import unittest
import json
from pathlib import Path

from godot_input_auditor.cli import main


class CliTests(unittest.TestCase):
    def test_cli_prints_version(self) -> None:
        stdout = StringIO()

        with self.assertRaises(SystemExit) as raised:
            with redirect_stdout(stdout):
                main(["--version"])

        self.assertEqual(raised.exception.code, 0)
        self.assertIn("godot-input-audit 0.1.1", stdout.getvalue())

    def test_cli_generates_docs_and_constants(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / "project.godot").write_text(
                """
[input]
confirm={
"events": [Object(InputEventKey,"physical_keycode":13)]
}
""",
                encoding="utf-8",
            )
            docs = project / "docs" / "INPUT_REFERENCE.md"
            constants = project / "scripts" / "generated" / "input_actions.gd"

            exit_code = main(
                [
                    str(project),
                    "--require",
                    "keyboard,touch",
                    "--write-docs",
                    str(docs),
                    "--generate-gd",
                    str(constants),
                ]
            )

            self.assertEqual(exit_code, 1)
            self.assertIn("confirm", docs.read_text(encoding="utf-8"))
            self.assertIn('CONFIRM = "confirm"', constants.read_text(encoding="utf-8"))

    def test_cli_outputs_sarif_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / "project.godot").write_text(
                """
[input]
confirm={
"events": [Object(InputEventKey,"physical_keycode":13)]
}
""",
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main([str(project), "--require", "keyboard,touch", "--format", "sarif", "--fail-on", "none"])

            sarif = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(sarif["version"], "2.1.0")
            driver = sarif["runs"][0]["tool"]["driver"]
            self.assertEqual(driver["name"], "godot-input-map-auditor")
            self.assertTrue(driver["rules"])
            self.assertTrue(sarif["runs"][0]["results"])

    def test_cli_rejects_unknown_required_device_family(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / "project.godot").write_text("[input]\n", encoding="utf-8")

            with self.assertRaises(SystemExit) as raised:
                main([str(project), "--require", "keyboard,steamdeck"])

            self.assertEqual(raised.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
