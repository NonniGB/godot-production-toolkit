import unittest

from godot_input_auditor.input_parser import parse_input_map


PROJECT = """
config_version=5

[input]
move_left={
"deadzone": 0.5,
"events": [Object(InputEventKey,"physical_keycode":65), Object(InputEventJoypadButton,"button_index":14)]
}
tap_select={
"deadzone": 0.5,
"events": [Object(InputEventScreenTouch,"index":0)]
}
zoom={
"deadzone": 0.5,
"events": [Object(InputEventMouseButton,"button_index":4)]
}

[rendering]
renderer/rendering_method="mobile"
"""


class ParserTests(unittest.TestCase):
    def test_parses_actions_and_classifies_device_families(self) -> None:
        actions = parse_input_map(PROJECT)
        by_name = {action.name: action for action in actions}

        self.assertEqual(set(by_name), {"move_left", "tap_select", "zoom"})
        self.assertEqual(by_name["move_left"].devices, {"keyboard", "gamepad"})
        self.assertEqual(by_name["tap_select"].devices, {"touch"})
        self.assertEqual(by_name["zoom"].devices, {"mouse"})

    def test_returns_empty_list_when_input_section_missing(self) -> None:
        self.assertEqual(parse_input_map("config_version=5\n"), [])


if __name__ == "__main__":
    unittest.main()
