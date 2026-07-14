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
            self.assertEqual(report["version"], "0.1.6")
            self.assertEqual(report["metadata"]["schema_version"], "1.1")
            self.assertIn("suggestion", report["findings"][0])
            self.assertIn("module_boundary_violation", report["rule_help"])

    def test_reports_hotspots_and_likely_unreferenced_scripts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scenes").mkdir()
            (root / "scripts" / "ui").mkdir(parents=True)
            (root / "scripts" / "gameplay").mkdir(parents=True)
            (root / "scripts" / "shared").mkdir(parents=True)
            (root / "scripts" / "autoload").mkdir(parents=True)
            (root / "scripts" / "ui" / "menu.gd").write_text(
                'extends Control\nconst Format = preload("res://scripts/shared/formatting.gd")\nfunc _ready() -> void:\n    GameState.reset()\n    GameState.save()\n',
                encoding="utf-8",
            )
            (root / "scripts" / "gameplay" / "inventory.gd").write_text(
                'extends RefCounted\nconst Format = preload("res://scripts/shared/formatting.gd")\n',
                encoding="utf-8",
            )
            (root / "scripts" / "shared" / "formatting.gd").write_text("extends RefCounted\n", encoding="utf-8")
            (root / "scripts" / "shared" / "orphan.gd").write_text("extends RefCounted\n", encoding="utf-8")
            (root / "scripts" / "shared" / "global_type.gd").write_text(
                "class_name GlobalType\nextends RefCounted\n",
                encoding="utf-8",
            )
            (root / "scripts" / "autoload" / "game_state.gd").write_text("extends Node\n", encoding="utf-8")
            (root / "project.godot").write_text(
                '[autoload]\nGameState="*res://scripts/autoload/game_state.gd"\n',
                encoding="utf-8",
            )
            (root / "scenes" / "menu.tscn").write_text(
                '[gd_scene load_steps=2 format=3]\n[ext_resource type="Script" path="res://scripts/ui/menu.gd" id="1"]\n[node name="Menu" type="Control"]\nscript = ExtResource("1")\n',
                encoding="utf-8",
            )
            config = root / "architecture-guard.toml"
            config.write_text(
                """
[modules.ui]
paths = ["scripts/ui/**"]
may_depend_on = ["shared"]
allowed_autoloads = ["GameState"]

[modules.gameplay]
paths = ["scripts/gameplay/**"]
may_depend_on = ["shared"]
allowed_autoloads = []

[modules.shared]
paths = ["scripts/shared/**"]
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
            hotspot_paths = [row["path"] for row in report["hotspots"]]
            possible_unused_paths = [row["path"] for row in report["possible_unused_scripts"]]
            self.assertEqual(exit_code, 0)
            self.assertIn("scripts/shared/formatting.gd", hotspot_paths)
            self.assertIn("scripts/shared/orphan.gd", possible_unused_paths)
            self.assertNotIn("scripts/shared/global_type.gd", possible_unused_paths)
            self.assertNotIn("scripts/autoload/game_state.gd", possible_unused_paths)
            self.assertEqual(report["summary"]["possible_unused_scripts"], 2)
            summaries = {row["module"]: row for row in report["owner_summaries"]}
            self.assertEqual(report["summary"]["owner_summaries"], 4)
            self.assertEqual(summaries["shared"]["matched_scripts"], 3)
            self.assertEqual(summaries["shared"]["incoming_dependencies"], 2)
            self.assertEqual(summaries["shared"]["possible_unused_scripts"], 1)
            self.assertEqual(summaries["ui"]["outgoing_dependencies"], 1)
            self.assertEqual(summaries["ui"]["autoload_references"], 2)
            self.assertEqual(summaries["<unowned>"]["matched_scripts"], 1)

    def test_reports_likely_unreferenced_resources(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "assets" / "sprites").mkdir(parents=True)
            (root / "assets" / "audio").mkdir(parents=True)
            (root / "scenes").mkdir()
            (root / "scripts").mkdir()
            (root / "scripts" / "main.gd").write_text(
                'extends Node\nconst Ship = preload("res://assets/sprites/ship.png")\n',
                encoding="utf-8",
            )
            (root / "scenes" / "main.tscn").write_text(
                '[gd_scene load_steps=2 format=3]\n'
                '[ext_resource type="Script" path="res://scripts/main.gd" id="1"]\n'
                '[node name="Main" type="Node"]\n'
                'script = ExtResource("1")\n',
                encoding="utf-8",
            )
            (root / "assets" / "sprites" / "ship.png").write_bytes(b"fake-png")
            (root / "assets" / "sprites" / "old_enemy.png").write_bytes(b"old-png")
            (root / "assets" / "audio" / "unused_alert.ogg").write_bytes(b"fake-ogg")
            (root / "project.godot").write_text(
                'config_version=5\n[application]\nrun/main_scene="res://scenes/main.tscn"\n',
                encoding="utf-8",
            )
            config = root / "architecture-guard.toml"
            config.write_text(
                """
[modules.main]
paths = ["scripts/**", "scenes/**", "assets/**"]
may_depend_on = []
""",
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main([str(root), "--config", str(config), "--format", "json", "--fail-on", "none"])

            report = json.loads(stdout.getvalue())
            unused_paths = [row["path"] for row in report["possible_unused_resources"]]
            self.assertEqual(exit_code, 0)
            self.assertEqual(report["version"], "0.1.6")
            self.assertEqual(report["summary"]["possible_unused_resources"], 2)
            self.assertIn("assets/sprites/old_enemy.png", unused_paths)
            self.assertIn("assets/audio/unused_alert.ogg", unused_paths)
            self.assertNotIn("assets/sprites/ship.png", unused_paths)
            self.assertNotIn("scenes/main.tscn", unused_paths)

    def test_reports_module_paths_that_match_no_scripts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scripts" / "ui").mkdir(parents=True)
            (root / "scripts" / "ui" / "menu.gd").write_text("extends Control\n", encoding="utf-8")
            config = root / "architecture-guard.toml"
            config.write_text(
                """
[modules.ui]
paths = ["scripts/ui/**", "scripts/deleted_ui/**"]
may_depend_on = []
""",
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main([str(root), "--config", str(config), "--format", "json", "--fail-on", "none"])

            report = json.loads(stdout.getvalue())
            finding = next(item for item in report["findings"] if item["rule_id"] == "module_path_without_scripts")
            self.assertEqual(exit_code, 0)
            self.assertEqual(finding["module"], "ui")
            self.assertEqual(finding["path"], "architecture-guard.toml")
            self.assertEqual(finding["target"], "scripts/deleted_ui/**")
            self.assertIn("suggestion", finding)

    def test_module_path_warning_sarif_points_to_policy_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scripts" / "ui").mkdir(parents=True)
            (root / "scripts" / "ui" / "menu.gd").write_text("extends Control\n", encoding="utf-8")
            config = root / "architecture-guard.toml"
            config.write_text(
                """
[modules.ui]
paths = ["scripts/missing/**"]
may_depend_on = []
""",
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main([str(root), "--config", str(config), "--format", "sarif", "--fail-on", "none"])

            payload = json.loads(stdout.getvalue())
            uri = payload["runs"][0]["results"][0]["locations"][0]["physicalLocation"]["artifactLocation"]["uri"]
            self.assertEqual(exit_code, 0)
            self.assertEqual(uri, "architecture-guard.toml")

    def test_module_path_warning_only_fails_on_warning_threshold(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scripts" / "ui").mkdir(parents=True)
            (root / "scripts" / "ui" / "menu.gd").write_text("extends Control\n", encoding="utf-8")
            config = root / "architecture-guard.toml"
            config.write_text(
                """
[modules.ui]
paths = ["scripts/missing/**"]
may_depend_on = []
""",
                encoding="utf-8",
            )

            stdout = StringIO()
            with redirect_stdout(stdout):
                error_exit = main([str(root), "--config", str(config), "--format", "json", "--fail-on", "error"])
            stdout = StringIO()
            with redirect_stdout(stdout):
                warning_exit = main([str(root), "--config", str(config), "--format", "json", "--fail-on", "warning"])

            self.assertEqual(error_exit, 0)
            self.assertEqual(warning_exit, 1)

    def test_sarif_includes_rule_descriptions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scripts" / "ui").mkdir(parents=True)
            (root / "scripts" / "ui" / "menu.gd").write_text(
                'const Missing = preload("res://scripts/missing.gd")\n',
                encoding="utf-8",
            )
            config = root / "architecture-guard.toml"
            config.write_text(
                """
[modules.ui]
paths = ["scripts/ui/**"]
may_depend_on = []
""",
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main([str(root), "--config", str(config), "--format", "sarif", "--fail-on", "none"])

            payload = json.loads(stdout.getvalue())
            rules = payload["runs"][0]["tool"]["driver"]["rules"]
            self.assertEqual(exit_code, 0)
            self.assertEqual(rules[0]["id"], "unresolved_resource")
            self.assertIn("Loaded resource does not exist", rules[0]["name"])

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

    def test_markdown_lists_hotspots_and_likely_unreferenced_scripts(self) -> None:
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
                exit_code = main([str(root), "--config", str(config), "--format", "markdown", "--fail-on", "none"])

            markdown = stdout.getvalue()
            self.assertEqual(exit_code, 0)
            self.assertIn("## Dependency Hotspots", markdown)
            self.assertIn("scripts/shared/formatting.gd", markdown)
            self.assertIn("## Possible Unused Scripts", markdown)
            self.assertIn("## Possible Unused Resources", markdown)
            self.assertIn("## Module Ownership Summary", markdown)
            self.assertIn("| ui | 1 |", markdown)
            self.assertIn("## Module Dependency Graph", markdown)
            self.assertIn("```mermaid", markdown)
            self.assertIn("flowchart LR", markdown)
            self.assertIn("ui --> shared", markdown)

    def test_policy_ignore_paths_excludes_generated_scripts_and_resources(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scripts" / "main").mkdir(parents=True)
            (root / "scripts" / "generated").mkdir(parents=True)
            (root / "assets" / "generated").mkdir(parents=True)
            (root / "scripts" / "main" / "menu.gd").write_text(
                'extends Node\nconst Generated = preload("res://scripts/generated/api.gd")\n'
                'const Icon = preload("res://assets/generated/icon.png")\n',
                encoding="utf-8",
            )
            (root / "scripts" / "generated" / "api.gd").write_text("extends RefCounted\n", encoding="utf-8")
            (root / "assets" / "generated" / "icon.png").write_bytes(b"fake-png")
            config = root / "architecture-guard.toml"
            config.write_text(
                """
ignore_paths = ["scripts/generated/**", "assets/generated/**"]

[modules.main]
paths = ["scripts/main/**"]
may_depend_on = []
""",
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main([str(root), "--config", str(config), "--format", "json", "--fail-on", "none"])

            report = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(report["summary"]["scripts"], 1)
            self.assertEqual(report["policy"]["ignore_paths"], ["scripts/generated/**", "assets/generated/**"])
            self.assertNotIn(
                "scripts/generated/api.gd",
                [row["path"] for row in report["possible_unused_scripts"]],
            )
            self.assertNotIn(
                "assets/generated/icon.png",
                [row["path"] for row in report["possible_unused_resources"]],
            )
            self.assertFalse(report["findings"])


if __name__ == "__main__":
    unittest.main()
