import unittest

from godot_export_doctor.models import ExportPreset
from godot_export_doctor.rules import evaluate_presets


class RuleTests(unittest.TestCase):
    def test_android_release_preset_requires_identity_version_path_and_abi(self) -> None:
        preset = ExportPreset(
            index=0,
            name="Android Release",
            platform="Android",
            runnable=False,
            export_path="",
            options={"package/unique_name": "", "version/code": 0, "version/name": ""},
        )

        findings = evaluate_presets([preset])
        rule_ids = {finding.rule_id for finding in findings}

        self.assertIn("missing_export_path", rule_ids)
        self.assertIn("android_package_id_missing", rule_ids)
        self.assertIn("android_version_missing", rule_ids)
        self.assertIn("android_abi_missing", rule_ids)

    def test_release_debug_options_are_flagged(self) -> None:
        preset = ExportPreset(
            index=1,
            name="Android Release",
            platform="Android",
            runnable=False,
            export_path="build/game.apk",
            options={
                "package/unique_name": "com.example.game",
                "version/code": 1,
                "version/name": "1.0.0",
                "architectures/arm64-v8a": True,
                "debug/export_remote_debug": True,
            },
        )

        findings = evaluate_presets([preset])

        self.assertIn("debug_option_enabled_in_release", {finding.rule_id for finding in findings})

    def test_secret_values_are_redacted(self) -> None:
        preset = ExportPreset(
            index=2,
            name="Android Release",
            platform="Android",
            runnable=False,
            export_path="build/game.apk",
            options={
                "package/unique_name": "com.example.game",
                "version/code": 1,
                "version/name": "1.0.0",
                "architectures/arm64-v8a": True,
                "keystore/release_password": "super-secret",
            },
        )

        findings = evaluate_presets([preset])
        secret_findings = [finding for finding in findings if finding.rule_id == "hardcoded_credential_value"]

        self.assertEqual(len(secret_findings), 1)
        self.assertNotIn("super-secret", secret_findings[0].message)
        self.assertIn("<redacted>", secret_findings[0].message)

    def test_known_secret_placeholders_can_be_allowed(self) -> None:
        preset = ExportPreset(
            index=3,
            name="Android Release",
            platform="Android",
            runnable=False,
            export_path="build/game.apk",
            options={
                "package/unique_name": "com.example.game",
                "version/code": 1,
                "version/name": "1.0.0",
                "architectures/arm64-v8a": True,
                "keystore/release_password": "<set-in-ci>",
            },
        )

        findings = evaluate_presets([preset], allowed_secret_patterns=[r"<.+>"])

        self.assertNotIn("hardcoded_credential_value", {finding.rule_id for finding in findings})


if __name__ == "__main__":
    unittest.main()
