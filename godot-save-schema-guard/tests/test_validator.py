import unittest

from godot_save_guard.validator import validate_json


SCHEMA = {
    "type": "object",
    "required": ["version", "credits", "ship"],
    "additionalProperties": False,
    "properties": {
        "version": {"type": "integer"},
        "credits": {"type": "number"},
        "ship": {
            "type": "object",
            "required": ["id"],
            "properties": {"id": {"type": "string"}},
        },
    },
}


class ValidatorTests(unittest.TestCase):
    def test_valid_json_passes(self) -> None:
        findings = validate_json({"version": 2, "credits": 125.5, "ship": {"id": "starter"}}, SCHEMA)

        self.assertEqual(findings, [])

    def test_missing_required_and_type_mismatch_fail(self) -> None:
        findings = validate_json({"version": "2", "credits": "125"}, SCHEMA)
        rule_ids = {finding.rule_id for finding in findings}

        self.assertIn("numeric_type_drift", rule_ids)
        self.assertIn("missing_required_property", rule_ids)
        self.assertIn("unexpected_property", {finding.rule_id for finding in validate_json({"version": 1, "credits": 1, "ship": {"id": "a"}, "debug": True}, SCHEMA)})


if __name__ == "__main__":
    unittest.main()
