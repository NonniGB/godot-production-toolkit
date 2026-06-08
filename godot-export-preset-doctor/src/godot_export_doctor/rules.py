from __future__ import annotations

import os
import re
from typing import Iterable

from .models import ExportPreset, Finding

ANDROID_ABI_KEYS = (
    "architectures/arm64-v8a",
    "architectures/armeabi-v7a",
    "architectures/x86_64",
    "architectures/x86",
)

SECRET_KEY_RE = re.compile(r"(password|passphrase|secret|token)", re.IGNORECASE)
KEYSTORE_PATH_RE = re.compile(r"(keystore|codesign).*(path|file|release)", re.IGNORECASE)
ANDROID_PACKAGE_RE = re.compile(r"^[a-zA-Z][\w]*(\.[a-zA-Z][\w]*)+$")


def evaluate_presets(
    presets: Iterable[ExportPreset],
    *,
    platform: str | None = None,
    required_android_abis: Iterable[str] | None = None,
    allowed_secret_patterns: Iterable[str] | None = None,
) -> list[Finding]:
    required_abis = tuple(required_android_abis or ())
    secret_patterns = tuple(_compile_patterns(allowed_secret_patterns or ()))
    findings: list[Finding] = []
    for preset in presets:
        if platform and preset.platform.lower() != platform.lower():
            continue
        findings.extend(_generic_findings(preset))
        findings.extend(_credential_findings(preset, secret_patterns))
        if _is_release_like(preset):
            findings.extend(_release_findings(preset))
        if preset.platform.lower() == "android":
            findings.extend(_android_findings(preset, required_abis))
    return findings


def missing_export_presets_finding() -> Finding:
    return Finding(
        rule_id="missing_export_presets",
        severity="error",
        preset_index=None,
        preset_name="project",
        message="No export_presets.cfg file was found.",
    )


def _generic_findings(preset: ExportPreset) -> list[Finding]:
    findings: list[Finding] = []
    if not preset.name.strip():
        findings.append(_finding(preset, "missing_preset_name", "warning", "Preset name is missing."))
    if not preset.platform.strip():
        findings.append(_finding(preset, "missing_platform", "error", "Preset platform is missing."))
    if not preset.export_path.strip():
        findings.append(_finding(preset, "missing_export_path", "error", "Export path is missing."))
    return findings


def _credential_findings(preset: ExportPreset, allowed_secret_patterns: tuple[re.Pattern[str], ...]) -> list[Finding]:
    findings: list[Finding] = []
    for key, value in preset.options.items():
        if not isinstance(value, str) or not value:
            continue
        if (
            SECRET_KEY_RE.search(key)
            and not _looks_like_env_reference(value)
            and not _matches_allowed_secret_pattern(value, allowed_secret_patterns)
        ):
            findings.append(
                _finding(
                    preset,
                    "hardcoded_credential_value",
                    "error",
                    f"Option '{key}' contains a hard-coded credential value: <redacted>.",
                    option=key,
                )
            )
        elif KEYSTORE_PATH_RE.search(key) and _looks_like_local_path(value):
            findings.append(
                _finding(
                    preset,
                    "hardcoded_keystore_path",
                    "warning",
                    f"Option '{key}' points to a local keystore path. Prefer CI secrets or env vars.",
                    option=key,
                )
            )
    return findings


def _release_findings(preset: ExportPreset) -> list[Finding]:
    findings: list[Finding] = []
    for key, value in preset.options.items():
        if "debug" in key.lower() and _truthy(value):
            findings.append(
                _finding(
                    preset,
                    "debug_option_enabled_in_release",
                    "warning",
                    f"Release-like preset has debug option '{key}' enabled.",
                    option=key,
                )
            )
    return findings


def _android_findings(preset: ExportPreset, required_android_abis: tuple[str, ...]) -> list[Finding]:
    findings: list[Finding] = []
    package_id = str(preset.options.get("package/unique_name", "")).strip()
    version_code = preset.options.get("version/code")
    version_name = str(preset.options.get("version/name", "")).strip()

    if not package_id:
        findings.append(
            _finding(
                preset,
                "android_package_id_missing",
                "error",
                "Android package/unique_name is missing.",
                option="package/unique_name",
            )
        )
    elif not ANDROID_PACKAGE_RE.match(package_id):
        findings.append(
            _finding(
                preset,
                "android_package_id_invalid",
                "error",
                f"Android package/unique_name '{package_id}' is not a valid dotted package id.",
                option="package/unique_name",
            )
        )
    elif package_id in {"com.example.game", "org.godotengine.$genname"}:
        findings.append(
            _finding(
                preset,
                "android_package_id_placeholder",
                "warning",
                "Android package/unique_name still looks like a placeholder value.",
                option="package/unique_name",
            )
        )

    if not isinstance(version_code, int) or version_code < 1 or not version_name:
        findings.append(
            _finding(
                preset,
                "android_version_missing",
                "error",
                "Android version/code must be >= 1 and version/name must be set.",
            )
        )

    enabled_abis = {key for key in ANDROID_ABI_KEYS if _truthy(preset.options.get(key))}
    if required_android_abis:
        missing = [abi for abi in required_android_abis if abi not in enabled_abis]
        if missing:
            findings.append(
                _finding(
                    preset,
                    "android_required_abi_missing",
                    "error",
                    f"Android preset is missing required ABI(s): {', '.join(missing)}.",
                )
            )
    elif not enabled_abis:
        findings.append(
            _finding(
                preset,
                "android_abi_missing",
                "error",
                "Android preset has no enabled CPU architecture.",
            )
        )

    icon_keys = [key for key in preset.options if key.startswith("launcher_icons/")]
    if not icon_keys or not any(str(preset.options.get(key, "")).strip() for key in icon_keys):
        findings.append(
            _finding(
                preset,
                "android_launcher_icons_missing",
                "warning",
                "Android launcher icon options are missing or empty.",
            )
        )

    return findings


def _finding(
    preset: ExportPreset,
    rule_id: str,
    severity: str,
    message: str,
    *,
    option: str | None = None,
) -> Finding:
    return Finding(
        rule_id=rule_id,
        severity=severity,
        preset_index=preset.index,
        preset_name=preset.display_name(),
        message=message,
        option=option,
    )


def _is_release_like(preset: ExportPreset) -> bool:
    text = f"{preset.name} {preset.export_path}".lower()
    return "release" in text or not preset.runnable


def _truthy(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, int | float):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "enabled", "on"}
    return False


def _looks_like_env_reference(value: str) -> bool:
    stripped = value.strip()
    return (
        stripped.startswith("$")
        or stripped.startswith("%")
        or "${" in stripped
        or stripped.upper().startswith("ENV:")
    )


def _looks_like_local_path(value: str) -> bool:
    return os.path.isabs(value) or ":" in value or "\\" in value


def _compile_patterns(patterns: Iterable[str]) -> list[re.Pattern[str]]:
    compiled: list[re.Pattern[str]] = []
    for pattern in patterns:
        try:
            compiled.append(re.compile(str(pattern)))
        except re.error:
            continue
    return compiled


def _matches_allowed_secret_pattern(value: str, patterns: tuple[re.Pattern[str], ...]) -> bool:
    return any(pattern.fullmatch(value.strip()) for pattern in patterns)
