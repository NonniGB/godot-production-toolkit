import unittest
from pathlib import Path

from godot_save_guard.migration import build_migration_command


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


if __name__ == "__main__":
    unittest.main()
