import tempfile
import unittest
from pathlib import Path

from godot_visual_smoke.config import load_config, load_viewport_manifest


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

    def test_loads_external_viewport_manifest_from_settings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = root / "viewports.toml"
            config_path = root / "visual-smoke.toml"
            manifest.write_text(
                """
[viewports.portrait_phone]
width = 720
height = 1280
safe_area = { top = 48, bottom = 24 }
""",
                encoding="utf-8",
            )
            config_path.write_text(
                """
[settings]
viewport_manifest = "viewports.toml"

[[scenes]]
name = "menu"
path = "res://scenes/menu.tscn"
viewport = "portrait_phone"
""",
                encoding="utf-8",
            )

            config = load_config(config_path)

            self.assertEqual(config.viewports["portrait_phone"].height, 1280)
            self.assertEqual(config.viewports["portrait_phone"].safe_area.top, 48)
            self.assertEqual(config.viewports["portrait_phone"].safe_area.bottom, 24)

    def test_inline_viewports_override_manifest_viewports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = root / "viewports.toml"
            config_path = root / "visual-smoke.toml"
            manifest.write_text(
                """
[viewports.phone]
width = 720
height = 1280
""",
                encoding="utf-8",
            )
            config_path.write_text(
                """
[viewports.phone]
width = 800
height = 1200
""",
                encoding="utf-8",
            )

            config = load_config(config_path, viewport_manifest=manifest)

            self.assertEqual(config.viewports["phone"].width, 800)
            self.assertEqual(config.viewports["phone"].height, 1200)

    def test_loads_viewport_manifest_directly(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest = Path(tmp) / "viewports.toml"
            manifest.write_text(
                """
[viewports.tablet]
width = 1536
height = 2048
safe_area = { left = 12, right = 12 }
""",
                encoding="utf-8",
            )

            viewports = load_viewport_manifest(manifest)

            self.assertEqual(viewports["tablet"].safe_area.left, 12)
            self.assertEqual(viewports["tablet"].safe_area.right, 12)


if __name__ == "__main__":
    unittest.main()
