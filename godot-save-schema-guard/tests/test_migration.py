import unittest
from pathlib import Path

from godot_save_guard.migration import build_chain_commands, build_migration_command, parse_migration_chain


class MigrationTests(unittest.TestCase):
    def test_builds_command_from_input_output_template(self) -> None:
        command = build_migration_command(
            "godot --headless --script migrate.gd --input {input} --output {output}",
            Path("old/save.json"),
            Path("new/save.json"),
        )

        self.assertEqual(
            command,
            f"godot --headless --script migrate.gd --input {Path('old/save.json')} --output {Path('new/save.json')}",
        )

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


if __name__ == "__main__":
    unittest.main()
