import json
import sys
import tempfile
import unittest
from pathlib import Path

from godot_save_guard.migration import (
    analyze_migration_graph,
    build_chain_commands,
    build_migration_command,
    compare_migrated_fixture,
    parse_migration_chain,
    run_migration_command,
)


class MigrationTests(unittest.TestCase):
    def test_builds_command_from_input_output_template(self) -> None:
        command = build_migration_command(
            "godot --headless --script migrate.gd --input {input} --output {output}",
            Path("old/save.json"),
            Path("new/save.json"),
        )

        self.assertEqual(
            command,
            [
                "godot", "--headless", "--script", "migrate.gd", "--input",
                str(Path("old/save.json")), "--output", str(Path("new/save.json")),
            ],
        )

    def test_fixture_paths_remain_single_arguments(self) -> None:
        command = build_migration_command(
            "python migrate.py {input} {output}",
            Path("old saves/save & one.json"),
            Path("new saves/save;one.json"),
        )

        self.assertEqual(command[2], str(Path("old saves/save & one.json")))
        self.assertEqual(command[3], str(Path("new saves/save;one.json")))

    def test_empty_or_unbalanced_command_template_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            build_migration_command("   ", Path("old.json"), Path("new.json"))
        with self.assertRaises(ValueError):
            build_migration_command('python "unterminated', Path("old.json"), Path("new.json"))

    def test_parses_ordered_migration_chain(self) -> None:
        steps = parse_migration_chain(
            {
                "steps": [
                    {"from": 1, "to": 2, "command": "migrate-v1-v2 {input} {output}"},
                    {"from": 2, "to": 3, "command": "migrate-v2-v3 {input} {output}"},
                ]
            }
        )

        self.assertEqual([step.label for step in steps], ["1->2", "2->3"])

    def test_builds_chain_commands_with_intermediate_outputs(self) -> None:
        steps = parse_migration_chain(
            {
                "steps": [
                    {"from": "1", "to": "2", "command": "copy {input} {output}"},
                    {"from": "2", "to": "3", "command": "copy {input} {output}"},
                ]
            }
        )

        commands = build_chain_commands(steps, Path("fixtures/save.json"), Path("migrated"))

        self.assertEqual(commands[0][2], Path("migrated/save.v2.json"))
        self.assertIn(str(Path("migrated/save.v2.json")), commands[1][3])
        self.assertEqual(commands[1][2], Path("migrated/save.v3.json"))

    def test_chain_preserves_nested_relative_path(self) -> None:
        steps = parse_migration_chain(
            {"steps": [{"from": "1", "to": "2", "command": "copy {input} {output}"}]}
        )

        commands = build_chain_commands(
            steps,
            Path("fixtures/profile-a/save.json"),
            Path("migrated"),
            Path("profile-a/save.json"),
        )

        self.assertEqual(commands[0][2], Path("migrated/profile-a/save.v2.json"))

    def test_missing_migration_executable_is_a_finding(self) -> None:
        finding = run_migration_command(["definitely-not-a-real-migration-command"])

        self.assertIsNotNone(finding)
        self.assertEqual(finding.rule_id, "migration_command_unavailable")

    def test_migration_timeout_is_a_finding(self) -> None:
        finding = run_migration_command(
            [sys.executable, "-c", "import time; time.sleep(2)"],
            timeout=1,
            capture_output=True,
        )

        self.assertIsNotNone(finding)
        self.assertEqual(finding.rule_id, "migration_command_timed_out")

    def test_analyzes_supported_versions_that_cannot_reach_current(self) -> None:
        steps = parse_migration_chain(
            {
                "steps": [
                    {"from": "1", "to": "2", "command": "copy {input} {output}"},
                    {"from": "3", "to": "4", "command": "copy {input} {output}"},
                ]
            }
        )

        findings = analyze_migration_graph(steps, current_version="4", supported_versions=["1", "3", "4"])

        self.assertEqual([finding.rule_id for finding in findings], ["migration_path_missing"])
        self.assertIn("version 1", findings[0].message)

    def test_compares_original_and_final_migrated_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            original = root / "save.v1.json"
            migrated = root / "save.v3.json"
            original.write_text(
                json.dumps({"version": 1, "credits": 100, "debug": True}),
                encoding="utf-8",
            )
            migrated.write_text(
                json.dumps({"version": 3, "credits": 125, "inventory": ["laser"]}),
                encoding="utf-8",
            )

            finding = compare_migrated_fixture(original, migrated)

            self.assertEqual(finding.rule_id, "migration_compare_summary")
            self.assertEqual(finding.severity, "info")
            self.assertIn("version 1 -> 3", finding.message)
            self.assertIn("added 1", finding.message)
            self.assertIn("removed 1", finding.message)
            self.assertIn("changed 2", finding.message)
            self.assertIn("$.inventory", finding.message)
            self.assertIn("$.debug", finding.message)

    def test_failed_migration_command_can_capture_output_snippets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            script = root / "fail.py"
            script.write_text(
                "import sys\n"
                "print('started migration')\n"
                "print('missing field credits', file=sys.stderr)\n"
                "raise SystemExit(7)\n",
                encoding="utf-8",
            )

            finding = run_migration_command(f'"{sys.executable}" "{script}"', capture_output=True)

            self.assertIsNotNone(finding)
            assert finding is not None
            self.assertEqual(finding.rule_id, "migration_command_failed")
            self.assertIn("exit code 7", finding.message)
            self.assertIn("stdout: started migration", finding.message)
            self.assertIn("stderr: missing field credits", finding.message)


if __name__ == "__main__":
    unittest.main()
