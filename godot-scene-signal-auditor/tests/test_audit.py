import unittest
from pathlib import Path

from godot_signal_auditor.audit import audit_project_model
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


if __name__ == "__main__":
    unittest.main()
