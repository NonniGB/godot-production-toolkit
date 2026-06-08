from contextlib import redirect_stdout
from io import StringIO
import json
import tempfile
import unittest
from pathlib import Path

from godot_mobile_perf_doctor.cli import main


class CliTests(unittest.TestCase):
    def test_cli_prints_version(self) -> None:
        stdout = StringIO()

        with self.assertRaises(SystemExit) as raised:
            with redirect_stdout(stdout):
                main(["--version"])

        self.assertEqual(raised.exception.code, 0)
        self.assertIn("godot-mobile-perf-doctor 0.1.2", stdout.getvalue())

    def test_cli_writes_json_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "project.godot").write_text(
                """
[rendering]
renderer/rendering_method="forward_plus"
""",
                encoding="utf-8",
            )
            output = root / "report.json"

            exit_code = main([str(root), "--static", "--format", "json", "--output", str(output)])

            self.assertEqual(exit_code, 1)
            self.assertGreater(json.loads(output.read_text(encoding="utf-8"))["summary"]["warnings"], 0)

    def test_cli_outputs_sarif_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "project.godot").write_text(
                """
[rendering]
renderer/rendering_method="forward_plus"
""",
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main([str(root), "--static", "--format", "sarif", "--fail-on", "none"])

            sarif = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(sarif["version"], "2.1.0")
            driver = sarif["runs"][0]["tool"]["driver"]
            self.assertEqual(driver["name"], "godot-mobile-perf-doctor")
            self.assertTrue(driver["rules"])
            self.assertTrue(sarif["runs"][0]["results"])

    def test_cli_uses_config_file_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".godot-mobile-perf-doctor.toml").write_text(
                "\n".join(
                    [
                        'format = "json"',
                        'fail_on = "none"',
                        "max_viewport_pixels = 1000",
                    ]
                ),
                encoding="utf-8",
            )
            (root / "project.godot").write_text(
                """
[display]
window/size/viewport_width=1280
window/size/viewport_height=720
""",
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main([str(root), "--static"])

            report = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertIn("large_base_viewport", {finding["rule_id"] for finding in report["findings"]})


if __name__ == "__main__":
    unittest.main()
