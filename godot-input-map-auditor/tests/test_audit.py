import unittest

from godot_input_auditor.audit import evaluate_actions
from godot_input_auditor.models import InputAction, InputEvent


class AuditTests(unittest.TestCase):
    def test_missing_required_devices_are_reported(self) -> None:
        action = InputAction(
            name="confirm",
            events=[InputEvent(event_type="InputEventKey", device="keyboard", signature="key:13")],
        )

        findings = evaluate_actions([action], required_devices={"keyboard", "touch"})

        self.assertEqual(findings[0].rule_id, "missing_required_device")
        self.assertIn("touch", findings[0].message)

    def test_duplicate_bindings_are_reported(self) -> None:
        actions = [
            InputAction(
                name="move_left",
                events=[InputEvent(event_type="InputEventKey", device="keyboard", signature="key:65")],
            ),
            InputAction(
                name="menu_left",
                events=[InputEvent(event_type="InputEventKey", device="keyboard", signature="key:65")],
            ),
        ]

        findings = evaluate_actions(actions, required_devices=set())

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].rule_id, "duplicate_binding")
        self.assertIn("move_left", findings[0].message)
        self.assertIn("menu_left", findings[0].message)


if __name__ == "__main__":
    unittest.main()
