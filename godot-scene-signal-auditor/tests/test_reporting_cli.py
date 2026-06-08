from contextlib import redirect_stdout
from io import StringIO
import json
import tempfile
import unittest
from pathlib import Path

from godot_signal_auditor.cli import main
from godot_signal_auditor.models import ParsedScene, SceneConnection
from godot_signal_auditor.reporting import render_mermaid_graph


class ReportingCliTests(unittest.TestCase):
    def test_cli_prints_version(self) -> None:
        stdout = StringIO()

        with self.assertRaises(SystemExit) as raised:
            with redirect_stdout(stdout):
                main(["--version"])

        self.assertEqual(raised.exception.code, 0)
        self.assertIn("godot-signal-audit 0.1.0", stdout.getvalue())

    def test_mermaid_graph_contains_signal_edge(self) -> None:
        scene = ParsedScene(
            path=Path("scenes/menu.tscn"),
            node_scripts={},
            connections=[SceneConnection(Path("scenes/menu.tscn"), "pressed", "StartButton", ".", "_on_start_pressed")],
        )

        graph = render_mermaid_graph([scene])

        self.assertIn("flowchart LR", graph)
        self.assertIn('"StartButton" -->|"pressed / _on_start_pressed"| "."', graph)

    def test_cli_writes_json_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scenes").mkdir()
            (root / "scripts").mkdir()
            (root / "scripts" / "menu.gd").write_text("func _ready() -> void:\n    pass\n", encoding="utf-8")
            (root / "scenes" / "menu.tscn").write_text(
                """
[gd_scene format=3]
[ext_resource type="Script" path="res://scripts/menu.gd" id="1_menu"]
[node name="Menu" type="Control"]
script = ExtResource("1_menu")
[connection signal="pressed" from="StartButton" to="." method="_on_missing"]
""",
                encoding="utf-8",
            )
            output = root / "report.json"

            exit_code = main([str(root), "--strict-stale-connections", "--format", "json", "--output", str(output)])

            self.assertEqual(exit_code, 1)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["summary"]["errors"], 1)


if __name__ == "__main__":
    unittest.main()
