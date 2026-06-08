import tempfile
import unittest
from pathlib import Path

from godot_visual_smoke.config import load_config


class ConfigTests(unittest.TestCase):
    def test_loads_scene_and_viewport_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "visual-smoke.toml"
            path.write_text(
                """
[settings]
pixel_tolerance = 2
max_changed_percent = 0.5

[viewports.portrait_phone]
width = 720
height = 1280

[[scenes]]
name = "menu"
path = "res://scenes/menu.tscn"
viewport = "portrait_phone"
""",
                encoding="utf-8",
            )

            config = load_config(path)

            self.assertEqual(config.pixel_tolerance, 2)
            self.assertEqual(config.max_changed_percent, 0.5)
            self.assertEqual(config.viewports["portrait_phone"].width, 720)
            self.assertEqual(config.scenes[0].path, "res://scenes/menu.tscn")


if __name__ == "__main__":
    unittest.main()
