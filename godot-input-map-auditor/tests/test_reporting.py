import json
import unittest

from godot_input_auditor.models import InputAction, InputEvent
from godot_input_auditor.reporting import (
    render_gdscript_constants,
    render_json_report,
    render_markdown_reference,
)


class ReportingTests(unittest.TestCase):
    def test_markdown_reference_lists_actions_and_devices(self) -> None:
        action = InputAction(
            name="move_left",
            events=[InputEvent(event_type="InputEventKey", device="keyboard", signature="key:65")],
        )

        markdown = render_markdown_reference([action])

        self.assertIn("# Input Reference", markdown)
        self.assertIn("| move_left | keyboard | 1 |", markdown)

    def test_gdscript_constants_are_generated(self) -> None:
        actions = [InputAction(name="move_left", events=[]), InputAction(name="ui_accept", events=[])]

        gdscript = render_gdscript_constants(actions)

        self.assertIn('const MOVE_LEFT = "move_left"', gdscript)
        self.assertIn('const UI_ACCEPT = "ui_accept"', gdscript)

    def test_json_report_contains_summary(self) -> None:
        action = InputAction(name="tap", events=[InputEvent("InputEventScreenTouch", "touch", "touch:0")])

        report = json.loads(render_json_report([action], []))

        self.assertEqual(report["summary"]["actions"], 1)
        self.assertEqual(report["actions"][0]["devices"], ["touch"])


if __name__ == "__main__":
    unittest.main()
