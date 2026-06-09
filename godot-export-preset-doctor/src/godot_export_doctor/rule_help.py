from __future__ import annotations


RULE_HELP: dict[str, dict[str, str]] = {
    "android_abi_missing": {
        "title": "Android ABI missing",
        "explanation": "The Android preset has no enabled CPU architecture, so exported APK/AAB builds may not run on target devices.",
    },
    "android_launcher_icons_missing": {
        "title": "Android launcher icons missing",
        "explanation": "Launcher icon fields are empty or absent, which can leave the exported app with incomplete store/device branding.",
    },
    "android_package_id_invalid": {
        "title": "Android package id invalid",
        "explanation": "Android package ids must be dotted identifiers such as com.example.game.",
    },
    "android_package_id_missing": {
        "title": "Android package id missing",
        "explanation": "Android exports need a stable package id before they can be installed, updated, or published reliably.",
    },
    "android_package_id_placeholder": {
        "title": "Android package id placeholder",
        "explanation": "Placeholder package ids are easy to ship accidentally and can block later store/update workflows.",
    },
    "android_required_abi_missing": {
        "title": "Required Android ABI missing",
        "explanation": "The preset does not enable one of the ABI families required by the project or CI policy.",
    },
    "android_version_missing": {
        "title": "Android version missing",
        "explanation": "Android releases need a positive version code and visible version name for install and store workflows.",
    },
    "debug_option_enabled_in_release": {
        "title": "Debug option enabled in release",
        "explanation": "Release-like presets should not keep debug options enabled unless the build is intentionally diagnostic.",
    },
    "hardcoded_credential_value": {
        "title": "Hard-coded credential value",
        "explanation": "Signing passwords, tokens, and secrets should usually come from CI secrets or environment variables.",
    },
    "hardcoded_keystore_path": {
        "title": "Local keystore path",
        "explanation": "Local signing paths tend to fail in CI and can expose machine-specific release setup in shared files.",
    },
    "missing_export_path": {
        "title": "Missing export path",
        "explanation": "Export jobs need a target path so CI and local release scripts know where the build artifact should be written.",
    },
    "missing_export_presets": {
        "title": "Missing export presets",
        "explanation": "No export_presets.cfg file was found, so release preset readiness cannot be checked.",
    },
    "missing_platform": {
        "title": "Missing platform",
        "explanation": "Each preset needs a platform so release tooling can tell which exporter it targets.",
    },
    "missing_preset_name": {
        "title": "Missing preset name",
        "explanation": "Named presets are easier to review, select in CI, and discuss in release notes.",
    },
}


def explain_rule(rule_id: str) -> dict[str, str]:
    return RULE_HELP.get(
        rule_id,
        {
            "title": rule_id.replace("_", " ").title(),
            "explanation": "This export preset rule reported a project-specific issue.",
        },
    )


def catalog_for(rule_ids: set[str]) -> dict[str, dict[str, str]]:
    return {rule_id: explain_rule(rule_id) for rule_id in sorted(rule_ids)}
