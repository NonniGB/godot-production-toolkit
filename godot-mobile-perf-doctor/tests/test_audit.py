import unittest

from godot_mobile_perf_doctor.audit import audit_settings


class AuditTests(unittest.TestCase):
    def test_flags_mobile_unfriendly_renderer_and_resolution(self) -> None:
        findings = audit_settings(
            {
                "rendering/renderer/rendering_method": "forward_plus",
                "display/window/size/viewport_width": 2560,
                "display/window/size/viewport_height": 1440,
                "display/window/stretch/mode": "disabled",
            },
            profile="portrait-2d",
        )
        rule_ids = {finding.rule_id for finding in findings}

        self.assertIn("forward_plus_renderer_mobile_risk", rule_ids)
        self.assertIn("large_base_viewport", rule_ids)
        self.assertIn("stretch_disabled", rule_ids)


if __name__ == "__main__":
    unittest.main()
