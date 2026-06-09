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
        self.assertIn("godot-mobile-perf-doctor 0.1.6", stdout.getvalue())

    def test_cli_lists_builtin_profiles(self) -> None:
        stdout = StringIO()

        with redirect_stdout(stdout):
            exit_code = main(["--list-profiles"])

        self.assertEqual(exit_code, 0)
        self.assertIn("portrait-2d", stdout.getvalue())
        self.assertIn("low-end-mobile", stdout.getvalue())

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
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(report["metadata"]["schema_version"], "1.1")
            self.assertEqual(report["metadata"]["tool_version"], "0.1.6")
            self.assertEqual(report["metadata"]["profile"], "portrait-2d")
            self.assertIn("Phone-first 2D", report["metadata"]["profile_description"])
            self.assertIn("forward_plus_renderer_mobile_risk", report["rules"])
            self.assertGreater(report["summary"]["warnings"], 0)

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
            self.assertEqual(driver["semanticVersion"], "0.1.6")
            self.assertTrue(driver["rules"])
            self.assertIn("Forward+ renderer selected", {rule["name"] for rule in driver["rules"]})
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
            self.assertEqual(report["metadata"]["limits"]["max_viewport_pixels"], 1000)
            self.assertIn("large_base_viewport", {finding["rule_id"] for finding in report["findings"]})

    def test_profile_defaults_set_budget_limits(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "project.godot").write_text(
                """
[display]
window/size/viewport_width=1600
window/size/viewport_height=900
window/stretch/mode="canvas_items"
""",
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main([str(root), "--static", "--profile", "low-end-mobile", "--format", "json"])

            report = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 1)
            self.assertEqual(report["metadata"]["profile"], "low-end-mobile")
            self.assertEqual(report["metadata"]["limits"]["max_texture_dimension"], 1024)
            self.assertIn("large_base_viewport", {finding["rule_id"] for finding in report["findings"]})

    def test_cli_reports_missing_project_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main([str(root), "--static", "--format", "json"])

            report = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 1)
            self.assertIn("missing_project_godot", {finding["rule_id"] for finding in report["findings"]})

    def test_cli_reports_invalid_config_as_usage_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / ".godot-mobile-perf-doctor.toml"
            config.write_text("format = [", encoding="utf-8")

            with self.assertRaises(SystemExit) as raised:
                main([str(root), "--config", str(config)])

            self.assertEqual(raised.exception.code, 2)

    def test_cli_rejects_invalid_config_choices(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cases = [
                'format = "xml"\n',
                'fail_on = "notice"\n',
            ]

            for contents in cases:
                with self.subTest(contents=contents):
                    config = root / ".godot-mobile-perf-doctor.toml"
                    config.write_text(contents, encoding="utf-8")

                    with self.assertRaises(SystemExit) as raised:
                        main([str(root), "--config", str(config)])

                    self.assertEqual(raised.exception.code, 2)

    def test_cli_rejects_non_positive_numeric_limits(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cases = [
                ["--max-texture-dimension", "0"],
                ["--max-viewport-pixels", "0"],
            ]

            for extra_args in cases:
                with self.subTest(extra_args=extra_args):
                    with self.assertRaises(SystemExit) as raised:
                        main([str(root), *extra_args])

                    self.assertEqual(raised.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
