import unittest
from pathlib import Path

from godot_signal_auditor.scene_parser import parse_scene


SCENE = """
[gd_scene load_steps=2 format=3]

[ext_resource type="Script" path="res://scripts/menu.gd" id="1_menu"]

[node name="Menu" type="Control" groups=["menu_root"]]
script = ExtResource("1_menu")

[node name="StartButton" type="Button" parent="." groups=["touch_target", "primary_action"]]

[connection signal="pressed" from="StartButton" to="." method="_on_start_pressed"]
"""


class SceneParserTests(unittest.TestCase):
    def test_parses_scene_connections_and_node_scripts(self) -> None:
        scene = parse_scene(Path("scenes/menu.tscn"), SCENE)

        self.assertEqual(scene.node_scripts["."], "scripts/menu.gd")
        self.assertEqual(len(scene.connections), 1)
        self.assertEqual(scene.node_groups["."], {"menu_root"})
        self.assertEqual(scene.node_groups["StartButton"], {"primary_action", "touch_target"})
        connection = scene.connections[0]
        self.assertEqual(connection.signal, "pressed")
        self.assertEqual(connection.from_node, "StartButton")
        self.assertEqual(connection.to_node, ".")
        self.assertEqual(connection.method, "_on_start_pressed")


if __name__ == "__main__":
    unittest.main()
