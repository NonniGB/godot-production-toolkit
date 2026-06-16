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
        self.assertIn("godot-export-doctor 0.1.9", stdout.getvalue())

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

    def test_cli_flags_can_require_abis_and_allow_secret_placeholders(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
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
architectures/armeabi-v7a=true
architectures/arm64-v8a=false
keystore/release_password="<set-in-ci>"
""",
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        str(project),
                        "--platform",
                        "Android",
                        "--required-android-abi",
                        "arm64-v8a",
                        "--allow-secret-pattern",
                        "<.+>",
                        "--format",
                        "json",
                        "--fail-on",
                        "warning",
                    ]
                )

            report = json.loads(stdout.getvalue())
            rule_ids = {finding["rule_id"] for finding in report["findings"]}
            self.assertEqual(exit_code, 1)
            self.assertIn("android_required_abi_missing", rule_ids)
            self.assertNotIn("hardcoded_credential_value", rule_ids)

    def test_cli_reports_invalid_config_as_usage_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            config = project / ".godot-export-doctor.toml"
            config.write_text("format = [", encoding="utf-8")

            with self.assertRaises(SystemExit) as raised:
                main([str(project), "--config", str(config)])

            self.assertEqual(raised.exception.code, 2)

    def test_cli_rejects_invalid_config_choices(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            cases = [
                'format = "xml"\n',
                'fail_on = "notice"\n',
            ]

            for contents in cases:
                with self.subTest(contents=contents):
                    config = project / ".godot-export-doctor.toml"
                    config.write_text(contents, encoding="utf-8")

                    with self.assertRaises(SystemExit) as raised:
                        main([str(project), "--config", str(config)])

                    self.assertEqual(raised.exception.code, 2)

    def test_cli_preserves_legacy_option_first_invocation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / "export_presets.cfg").write_text(
                """
[preset.0]
name="Web"
platform="Web"
export_path="build/web/index.html"
""",
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["--format", "json", str(project), "--fail-on", "none"])

            report = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(report["metadata"]["tool_version"], "0.1.9")
            self.assertEqual(report["summary"]["presets"], 1)

    def test_cli_matrix_reports_missing_expected_platform(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / "export_presets.cfg").write_text(
                """
[preset.0]
name="Android Release"
platform="Android"
export_path="build/game.apk"
custom_features="release,mobile"

[preset.0.options]
package/unique_name="com.example.game"
version/code=1
version/name="1.0.0"
architectures/arm64-v8a=true
""",
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "matrix",
                        str(project),
                        "--expected-platform",
                        "Android",
                        "--expected-platform",
                        "Web",
                        "--format",
                        "json",
                        "--fail-on",
                        "none",
                    ]
                )

            report = json.loads(stdout.getvalue())
            rules = {finding["rule_id"] for finding in report["findings"]}
            self.assertEqual(exit_code, 0)
            self.assertEqual(report["metadata"]["report_kind"], "export_matrix")
            self.assertIn("export_matrix_missing_platform", rules)

    def test_cli_leaks_reports_dev_files_and_local_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / "tests").mkdir()
            (project / "tests" / "debug_scene.tscn").write_text("[gd_scene]", encoding="utf-8")
            (project / "export_presets.cfg").write_text(
                """
[preset.0]
name="Windows Release"
platform="Windows Desktop"
export_filter="all_resources"
include_filter="*"
export_path="C:\\Users\\dev\\Desktop\\game.exe"
""",
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["leaks", str(project), "--format", "json", "--fail-on", "none"])

            report = json.loads(stdout.getvalue())
            rules = {finding["rule_id"] for finding in report["findings"]}
            self.assertEqual(exit_code, 0)
            self.assertIn("export_leak_dev_file", rules)
            self.assertIn("export_leak_local_path", rules)

    def test_cli_matrix_can_render_html(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / "export_presets.cfg").write_text(
                """
[preset.0]
name="Android Release"
platform="Android"
export_path="build/game.apk"
""",
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["matrix", str(project), "--format", "html", "--fail-on", "none"])

            html = stdout.getvalue()
            self.assertEqual(exit_code, 0)
            self.assertIn("<!doctype html>", html)
            self.assertIn("Godot Export Matrix", html)
            self.assertIn("Android Release", html)

    def test_cli_matrix_does_not_inherit_config_platform_filter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / ".godot-export-doctor.toml").write_text('platform = "Android"\n', encoding="utf-8")
            (project / "export_presets.cfg").write_text(
                """
[preset.0]
name="Android Release"
platform="Android"
export_path="build/game.apk"

[preset.1]
name="Web Release"
platform="Web"
export_path="build/web/index.html"
""",
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["matrix", str(project), "--format", "json", "--fail-on", "none"])

            report = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(report["summary"]["presets"], 2)
            self.assertEqual({row["platform"] for row in report["matrix"]}, {"Android", "Web"})

    def test_cli_diff_reports_changed_and_removed_presets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            baseline = root / "baseline"
            current = root / "current"
            baseline.mkdir()
            current.mkdir()
            (baseline / "export_presets.cfg").write_text(
                """
[preset.0]
name="Android Release"
platform="Android"
export_path="build/game.apk"

[preset.1]
name="Web Release"
platform="Web"
export_path="build/web/index.html"
""",
                encoding="utf-8",
            )
            (current / "export_presets.cfg").write_text(
                """
[preset.0]
name="Android Release"
platform="Android"
export_path="build/game.aab"
""",
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "diff",
                        str(current),
                        "--baseline",
                        str(baseline),
                        "--format",
                        "json",
                        "--fail-on",
                        "none",
                    ]
                )

            report = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(report["metadata"]["report_kind"], "export_diff")
            self.assertEqual(report["diff"]["changed"], ["Android Release"])
            self.assertEqual(report["diff"]["removed"], ["Web Release"])

    def test_cli_inspect_folder_reports_dev_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            export = Path(tmp) / "export"
            (export / "tests").mkdir(parents=True)
            (export / "tests" / "debug_scene.tscn").write_text("[gd_scene]", encoding="utf-8")
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["inspect-folder", str(export), "--format", "json", "--fail-on", "none"])

            report = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(report["metadata"]["report_kind"], "exported_folder_inspection")
            self.assertIn("exported_folder_dev_file", {finding["rule_id"] for finding in report["findings"]})

    def test_cli_diff_does_not_inherit_config_platform_filter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / ".godot-export-doctor.toml").write_text('platform = "Android"\n', encoding="utf-8")
            (project / "export_presets.cfg").write_text(
                """
[preset.0]
name="Android Release"
platform="Android"
export_path="build/game.apk"

[preset.1]
name="Web Release"
platform="Web"
export_path="build/web/index.html"
""",
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(
                    ["diff", str(project), "--baseline", str(project), "--format", "json", "--fail-on", "none"]
                )

            report = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(report["summary"]["removed"], 0)
            self.assertEqual(report["summary"]["changed"], 0)
            self.assertEqual(report["summary"]["presets"], 2)


if __name__ == "__main__":
    unittest.main()
