from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from godot_architecture_guard.cli import main


class ArchitectureGuardTests(unittest.TestCase):
    def test_reports_module_boundary_and_autoload_violations(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scripts" / "ui").mkdir(parents=True)
            (root / "scripts" / "gameplay").mkdir(parents=True)
            (root / "scripts" / "ui" / "menu.gd").write_text(
                'extends Control\nconst Inventory = preload("res://scripts/gameplay/inventory.gd")\nfunc _ready() -> void:\n    GameState.reset()\n',
                encoding="utf-8",
            )
            (root / "scripts" / "gameplay" / "inventory.gd").write_text("extends RefCounted\n", encoding="utf-8")
            config = root / "architecture-guard.toml"
            config.write_text(
                """
[modules.ui]
paths = ["scripts/ui/**"]
may_depend_on = []
allowed_autoloads = []

[modules.gameplay]
paths = ["scripts/gameplay/**"]
may_depend_on = []
allowed_autoloads = []

[autoloads]
names = ["GameState"]
""",
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main([str(root), "--config", str(config), "--format", "json", "--fail-on", "none"])

            report = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            rules = {finding["rule_id"] for finding in report["findings"]}
            self.assertIn("module_boundary_violation", rules)
            self.assertIn("autoload_access_violation", rules)

    def test_mermaid_lists_dependency_edges(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scripts" / "ui").mkdir(parents=True)
            (root / "scripts" / "shared").mkdir(parents=True)
            (root / "scripts" / "ui" / "menu.gd").write_text(
                'const Format = preload("res://scripts/shared/formatting.gd")\n',
                encoding="utf-8",
            )
            (root / "scripts" / "shared" / "formatting.gd").write_text("extends RefCounted\n", encoding="utf-8")
            config = root / "architecture-guard.toml"
            config.write_text(
                """
[modules.ui]
paths = ["scripts/ui/**"]
may_depend_on = ["shared"]

[modules.shared]
paths = ["scripts/shared/**"]
may_depend_on = []
""",
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main([str(root), "--config", str(config), "--format", "mermaid", "--fail-on", "none"])

            self.assertEqual(exit_code, 0)
            self.assertIn("flowchart LR", stdout.getvalue())
            self.assertIn("ui --> shared", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()

