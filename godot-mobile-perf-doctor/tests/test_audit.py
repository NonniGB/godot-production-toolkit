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

    def test_viewport_budget_is_configurable(self) -> None:
        findings = audit_settings(
            {
                "display/window/size/viewport_width": 1280,
                "display/window/size/viewport_height": 720,
                "display/window/stretch/mode": "canvas_items",
            },
            profile="portrait-2d",
            max_viewport_pixels=1000,
        )

        self.assertIn("large_base_viewport", {finding.rule_id for finding in findings})


if __name__ == "__main__":
    unittest.main()
