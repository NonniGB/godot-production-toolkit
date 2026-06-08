from contextlib import redirect_stdout
from io import StringIO
from contextlib import redirect_stdout
from io import StringIO
import json
import tempfile
import unittest
from pathlib import Path

from godot_export_doctor.cli import main


class CliTests(unittest.TestCase):
    def test_cli_prints_version(self) -> None:
        stdout = StringIO()

        with self.assertRaises(SystemExit) as raised:
            with redirect_stdout(stdout):
                main(["--version"])

        self.assertEqual(raised.exception.code, 0)
        self.assertIn("godot-export-doctor 0.1.2", stdout.getvalue())

    def test_cli_reports_findings_as_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / "export_presets.cfg").write_text(
                """
[preset.0]
name="Android Release"
platform="Android"
export_path=""

[preset.0.options]
package/unique_name=""
version/code=0
version/name=""
""",
                encoding="utf-8",
            )

            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main([str(project), "--format", "json", "--fail-on", "warning"])

            self.assertEqual(exit_code, 1)

    def test_cli_writes_output_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            output = project / "report.json"
            (project / "export_presets.cfg").write_text(
                """
[preset.0]
name="Web"
platform="Web"
export_path="build/web/index.html"
""",
                encoding="utf-8",
            )

            exit_code = main([str(project), "--format", "json", "--output", str(output)])

            self.assertEqual(exit_code, 0)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(report["summary"]["presets"], 1)
            self.assertEqual(report["summary"]["errors"], 0)

    def test_cli_config_can_allow_known_secret_placeholders(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / ".godot-export-doctor.toml").write_text(
                "\n".join(
                    [
                        'format = "json"',
                        'fail_on = "none"',
                        'allowed_secret_patterns = ["<.+>"]',
                    ]
                ),
                encoding="utf-8",
            )
            (project / "export_presets.cfg").write_text(
                """
[preset.0]
name="Android Release"
platform="Android"
export_path="build/game.apk"

[preset.0.options]
package/unique_name="com.example.game"
version/code=1
version/name="1.0.0"
architectures/arm64-v8a=true
keystore/release_password="<set-in-ci>"
""",
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main([str(project)])

            report = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertNotIn("hardcoded_credential_value", {finding["rule_id"] for finding in report["findings"]})


if __name__ == "__main__":
    unittest.main()
