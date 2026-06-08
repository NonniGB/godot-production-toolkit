import unittest

from godot_mobile_perf_doctor.project_settings import parse_project_settings


PROJECT = """
[rendering]
renderer/rendering_method="forward_plus"

[display]
window/size/viewport_width=2560
window/size/viewport_height=1440
window/stretch/mode="disabled"
"""


class ProjectSettingsTests(unittest.TestCase):
    def test_parses_project_godot_sections_and_values(self) -> None:
        settings = parse_project_settings(PROJECT)

        self.assertEqual(settings["rendering/renderer/rendering_method"], "forward_plus")
        self.assertEqual(settings["display/window/size/viewport_width"], 2560)
        self.assertEqual(settings["display/window/stretch/mode"], "disabled")


if __name__ == "__main__":
    unittest.main()
