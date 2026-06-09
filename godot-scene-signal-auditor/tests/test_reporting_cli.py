from contextlib import redirect_stdout
from io import StringIO
import json
import tempfile
import unittest
from pathlib import Path

from godot_signal_auditor.cli import main
from godot_signal_auditor.models import Finding, ParsedScene, ParsedScript, SceneConnection
from godot_signal_auditor.reporting import render_json_report, render_mermaid_graph, render_text_report


class ReportingCliTests(unittest.TestCase):
    def test_cli_prints_version(self) -> None:
        stdout = StringIO()

        with self.assertRaises(SystemExit) as raised:
            with redirect_stdout(stdout):
                main(["--version"])

        self.assertEqual(raised.exception.code, 0)
        self.assertIn("godot-signal-audit 0.1.2", stdout.getvalue())

    def test_mermaid_graph_contains_signal_edge(self) -> None:
        scene = ParsedScene(
            path=Path("scenes/menu.tscn"),
            node_scripts={},
            connections=[SceneConnection(Path("scenes/menu.tscn"), "pressed", "StartButton", ".", "_on_start_pressed")],
        )

        graph = render_mermaid_graph([scene])

        self.assertIn("flowchart LR", graph)
        self.assertIn('"StartButton" -->|"pressed / _on_start_pressed"| "."', graph)

    def test_json_report_includes_metadata_and_rule_help(self) -> None:
        report = json.loads(
            render_json_report(
                [],
                {},
                [Finding("stale_scene_connection", "error", Path("scenes/menu.tscn"), "Missing target method.")],
            )
        )

        self.assertEqual(report["metadata"]["schema_version"], "1.1")
        self.assertEqual(report["metadata"]["tool_version"], "0.1.2")
        self.assertEqual(report["rules"]["stale_scene_connection"]["title"], "Stale scene connection")
        self.assertIn("resolved target script", report["findings"][0]["explanation"])

    def test_text_report_includes_plain_language_rule_help(self) -> None:
        report = render_text_report(
            [],
            {"res://scripts/menu.gd": ParsedScript(Path("scripts/menu.gd"), set(), set())},
            [Finding("autoload_signal_usage", "warning", Path("scripts/menu.gd"), "Signal bus usage.")],
        )

        self.assertIn("[WARNING] Autoload signal connection: Signal bus usage.", report)
        self.assertIn("Why it matters:", report)

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
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(report["summary"]["errors"], 1)
            self.assertEqual(report["metadata"]["report_kind"], "scene_signal_audit")
            self.assertTrue(output.read_text(encoding="utf-8").endswith("\n"))


if __name__ == "__main__":
    unittest.main()
