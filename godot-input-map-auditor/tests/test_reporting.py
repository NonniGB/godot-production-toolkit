import json
import unittest

from godot_input_auditor.models import Finding, InputAction, InputEvent
from godot_input_auditor.policy import InputPolicy
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

        self.assertEqual(report["metadata"]["schema_version"], "1.1")
        self.assertEqual(report["metadata"]["tool_version"], "0.1.3")
        self.assertEqual(report["summary"]["actions"], 1)
        self.assertEqual(report["actions"][0]["devices"], ["touch"])

    def test_json_report_includes_rule_explanations(self) -> None:
        finding = Finding("missing_required_device", "error", "tap", "Input action 'tap' is missing touch.")

        report = json.loads(render_json_report([], [finding]))

        self.assertEqual(report["rules"]["missing_required_device"]["title"], "Required device missing")
        self.assertEqual(report["findings"][0]["title"], "Required device missing")
        self.assertIn("configured device families", report["findings"][0]["explanation"])

    def test_json_report_includes_policy_groups_when_provided(self) -> None:
        action = InputAction(name="move_left", events=[InputEvent("InputEventKey", "keyboard", "key:65")])
        policy = InputPolicy(
            action_groups={"movement": ["move_*"]},
            group_requirements={"movement": {"keyboard", "touch"}},
        )

        report = json.loads(render_json_report([action], [], policy=policy))

        self.assertEqual(report["summary"]["groups"], 1)
        self.assertEqual(report["actions"][0]["group"], "movement")
        self.assertEqual(report["actions"][0]["required_devices"], ["keyboard", "touch"])

    def test_markdown_reference_can_include_policy_groups(self) -> None:
        action = InputAction(name="ui_accept", events=[InputEvent("InputEventKey", "keyboard", "key:13")])
        policy = InputPolicy(action_groups={"menu": ["ui_*"]})

        markdown = render_markdown_reference([action], policy=policy)

        self.assertIn("| Action | Group | Devices | Events |", markdown)
        self.assertIn("| ui_accept | menu | keyboard | 1 |", markdown)


if __name__ == "__main__":
    unittest.main()
