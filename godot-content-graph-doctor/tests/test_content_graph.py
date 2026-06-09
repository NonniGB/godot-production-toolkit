from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from godot_content_graph_doctor.cli import main


class ContentGraphTests(unittest.TestCase):
    def test_json_report_finds_missing_reference_and_unused_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "data").mkdir()
            (root / "data" / "items.json").write_text(
                json.dumps(
                    [
                        {"id": "ore", "value": 2},
                        {"id": "bar", "value": 10},
                        {"id": "unused", "value": 100},
                    ]
                ),
                encoding="utf-8",
            )
            (root / "data" / "recipes.json").write_text(
                json.dumps(
                    [
                        {
                            "id": "smelt",
                            "craft_time": 3,
                            "inputs": [{"item": "ore"}],
                            "outputs": [{"item": "bar"}],
                        },
                        {
                            "id": "broken",
                            "craft_time": 40,
                            "inputs": [{"item": "missing"}],
                            "outputs": [{"item": "bar"}],
                        },
                    ]
                ),
                encoding="utf-8",
            )
            config = root / "content-graph.toml"
            config.write_text(
                """
[collections.items]
path = "data/items.json"
id = "id"
roots = ["ore"]
warn_unused = true
numeric_fields = ["value"]

[collections.recipes]
path = "data/recipes.json"
id = "id"
numeric_fields = ["craft_time"]

[[collections.recipes.references]]
field = "inputs[].item"
collection = "items"

[[collections.recipes.references]]
field = "outputs[].item"
collection = "items"
""",
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main([str(root), "--config", str(config), "--format", "json", "--fail-on", "none"])

            report = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(report["summary"]["collections"], 2)
            rule_ids = {finding["rule_id"] for finding in report["findings"]}
            self.assertIn("missing_reference", rule_ids)
            self.assertIn("unused_content", rule_ids)

    def test_mermaid_output_uses_configured_references_without_loading_godot(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / "content-graph.toml"
            config.write_text(
                """
[collections.items]
path = "items.csv"
id = "id"

[collections.recipes]
path = "recipes.csv"
id = "id"

[[collections.recipes.references]]
field = "output"
collection = "items"
""",
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main([str(root), "--config", str(config), "--format", "mermaid"])

            self.assertEqual(exit_code, 0)
            self.assertIn("flowchart LR", stdout.getvalue())
            self.assertIn("recipes -->|output| items", stdout.getvalue())

    def test_recipes_preset_runs_without_config_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "data").mkdir()
            (root / "data" / "items.json").write_text(
                json.dumps([{"id": "ore", "value": 2}, {"id": "bar", "value": 8}]),
                encoding="utf-8",
            )
            (root / "data" / "recipes.json").write_text(
                json.dumps(
                    [
                        {
                            "id": "smelt",
                            "inputs": [{"item": "ore"}],
                            "outputs": [{"item": "bar"}],
                            "craft_time": 4,
                        },
                        {
                            "id": "broken",
                            "inputs": [{"item": "missing"}],
                            "outputs": [{"item": "bar"}],
                            "craft_time": 5,
                        },
                    ]
                ),
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main([str(root), "--preset", "recipes", "--format", "json", "--fail-on", "none"])

            report = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(report["summary"]["collections"], 2)
            self.assertIn("recipes", report["collections"])
            self.assertIn("missing_reference", {finding["rule_id"] for finding in report["findings"]})

    def test_list_presets_prints_human_readable_preset_names(self) -> None:
        stdout = StringIO()

        with redirect_stdout(stdout):
            exit_code = main([".", "--list-presets"])

        self.assertEqual(exit_code, 0)
        self.assertIn("recipes", stdout.getvalue())
        self.assertIn("content-pack", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
