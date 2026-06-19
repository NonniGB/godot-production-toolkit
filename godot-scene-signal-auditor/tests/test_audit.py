import tempfile
import unittest
from pathlib import Path

from godot_signal_auditor.audit import audit_project_model
from godot_signal_auditor.contracts import audit_scene_contracts, compare_scene_contracts, load_contract
from godot_signal_auditor.models import ParsedScene, ParsedScript, SceneConnection


class AuditTests(unittest.TestCase):
    def test_stale_scene_connection_is_reported_when_target_method_missing(self) -> None:
        scene = ParsedScene(
            path=Path("scenes/menu.tscn"),
            node_scripts={".": "scripts/menu.gd"},
            connections=[
                SceneConnection(
                    scene_path=Path("scenes/menu.tscn"),
                    signal="pressed",
                    from_node="StartButton",
                    to_node=".",
                    method="_on_start_pressed",
                )
            ],
        )
        scripts = {"scripts/menu.gd": ParsedScript(Path("scripts/menu.gd"), signals=set(), methods={"_ready"}, connect_calls=[])}

        findings = audit_project_model([scene], scripts, strict_stale_connections=True)

        self.assertEqual(findings[0].rule_id, "stale_scene_connection")
        self.assertEqual(findings[0].severity, "error")

    def test_scene_contract_reports_missing_nodes_connections_methods_and_signals(self) -> None:
        scene = ParsedScene(
            path=Path("scenes/menu.tscn"),
            nodes={".", "StartButton"},
            node_scripts={".": "scripts/menu.gd"},
            connections=[
                SceneConnection(
                    scene_path=Path("scenes/menu.tscn"),
                    signal="pressed",
                    from_node="StartButton",
                    to_node=".",
                    method="_on_start_pressed",
                )
            ],
        )
        scripts = {
            "scripts/menu.gd": ParsedScript(
                Path("scripts/menu.gd"),
                signals={"ready_to_start"},
                methods={"_ready", "_on_start_pressed"},
                connect_calls=[],
            )
        }
        contract = {
            "scenes": [
                {
                    "path": "scenes/menu.tscn",
                    "required_nodes": [".", "MissingButton"],
                    "required_connections": [
                        {
                            "from": "StartButton",
                            "signal": "pressed",
                            "to": ".",
                            "method": "_on_start_pressed",
                        },
                        {
                            "from": "QuitButton",
                            "signal": "pressed",
                            "to": ".",
                            "method": "_on_quit_pressed",
                        },
                    ],
                    "script_methods": {".": ["_ready", "_on_quit_pressed"]},
                    "script_signals": {".": ["ready_to_start", "quit_requested"]},
                }
            ]
        }

        findings = audit_scene_contracts([scene], scripts, contract)

        self.assertEqual(
            [finding.message for finding in findings],
            [
                "Scene 'scenes/menu.tscn' is missing required node 'MissingButton'.",
                (
                    "Scene 'scenes/menu.tscn' is missing required connection "
                    "'QuitButton.pressed -> ._on_quit_pressed'."
                ),
                (
                    "Script 'scripts/menu.gd' for node '.' in scene 'scenes/menu.tscn' "
                    "is missing required method '_on_quit_pressed'."
                ),
                (
                    "Script 'scripts/menu.gd' for node '.' in scene 'scenes/menu.tscn' "
                    "is missing required signal 'quit_requested'."
                ),
            ],
        )
        self.assertTrue(all(finding.rule_id == "scene_contract_violation" for finding in findings))
        self.assertTrue(all(finding.severity == "error" for finding in findings))

    def test_scene_contract_reports_missing_groups_and_exported_properties(self) -> None:
        scene = ParsedScene(
            path=Path("scenes/menu.tscn"),
            nodes={".", "StartButton"},
            node_scripts={".": "scripts/menu.gd"},
            node_groups={".": {"menu_root"}, "StartButton": {"touch_target"}},
        )
        scripts = {
            "scripts/menu.gd": ParsedScript(
                Path("scripts/menu.gd"),
                signals=set(),
                methods={"_ready"},
                connect_calls=[],
                exported_properties={"title_text"},
            )
        }
        contract = {
            "scenes": [
                {
                    "path": "scenes/menu.tscn",
                    "node_groups": {
                        ".": ["menu_root", "modal"],
                        "StartButton": ["touch_target"],
                    },
                    "script_exports": {".": ["title_text", "theme_resource"]},
                }
            ]
        }

        findings = audit_scene_contracts([scene], scripts, contract)

        self.assertEqual(
            [finding.message for finding in findings],
            [
                "Node '.' in scene 'scenes/menu.tscn' is missing required group 'modal'.",
                (
                    "Script 'scripts/menu.gd' for node '.' in scene 'scenes/menu.tscn' "
                    "is missing required exported property 'theme_resource'."
                ),
            ],
        )

    def test_load_contract_reads_toml_scene_contracts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            contract_path = Path(tmp) / "scene-contract.toml"
            contract_path.write_text(
                """
[[scenes]]
path = "scenes/menu.tscn"
required_nodes = [".", "StartButton"]

[[scenes.required_connections]]
from = "StartButton"
signal = "pressed"
to = "."
method = "_ready"
""",
                encoding="utf-8",
            )

            contract = load_contract(contract_path)

            self.assertEqual(contract["scenes"][0]["path"], "scenes/menu.tscn")
            self.assertEqual(contract["scenes"][0]["required_nodes"], [".", "StartButton"])
            self.assertEqual(contract["scenes"][0]["required_connections"][0]["method"], "_ready")

    def test_contract_diff_reports_removed_targets_and_requirements(self) -> None:
        baseline = {
            "scenes": [
                {
                    "path": "scenes/menu.tscn",
                    "required_nodes": [".", "StartButton"],
                    "required_connections": [
                        {"from": "StartButton", "signal": "pressed", "to": ".", "method": "_on_start_pressed"}
                    ],
                    "script_methods": {".": ["_ready", "_on_start_pressed"]},
                    "script_signals": {".": ["menu_confirmed"]},
                    "script_exports": {".": ["menu_title"]},
                    "node_groups": {"StartButton": ["primary_action"]},
                },
                {"path": "scenes/options.tscn", "required_nodes": ["."]},
            ]
        }
        current = {"scenes": [{"path": "scenes/menu.tscn", "required_nodes": ["."]}]}

        findings = compare_scene_contracts(baseline, current)

        messages = [finding.message for finding in findings]
        self.assertTrue(all(finding.rule_id == "scene_contract_diff" for finding in findings))
        self.assertTrue(all(finding.severity == "warning" for finding in findings))
        self.assertIn("Scene contract target 'scenes/options.tscn' is not present in the current contract.", messages)
        self.assertIn("Current contract no longer requires node 'StartButton' for 'scenes/menu.tscn'.", messages)
        self.assertIn(
            "Current contract no longer requires connection 'StartButton.pressed -> ._on_start_pressed' for 'scenes/menu.tscn'.",
            messages,
        )
        self.assertIn(
            "Current contract no longer requires method '_on_start_pressed' on node '.' for 'scenes/menu.tscn'.",
            messages,
        )
        self.assertIn(
            "Current contract no longer requires signal 'menu_confirmed' on node '.' for 'scenes/menu.tscn'.",
            messages,
        )
        self.assertIn(
            "Current contract no longer requires exported property 'menu_title' on node '.' for 'scenes/menu.tscn'.",
            messages,
        )
        self.assertIn(
            "Current contract no longer requires group 'primary_action' on node 'StartButton' for 'scenes/menu.tscn'.",
            messages,
        )


if __name__ == "__main__":
    unittest.main()
