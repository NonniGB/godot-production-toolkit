from __future__ import annotations

import json

from . import __version__
from .models import AdbSummary, Finding, TextureSummary
from .profiles import get_profile
from .rule_help import catalog_for, explain_rule


def render_text_report(
    findings: list[Finding],
    textures: TextureSummary,
    adb: AdbSummary | None,
    *,
    profile: str,
    max_texture_dimension: int,
    max_viewport_pixels: int,
    mobile_ui_metadata: str | None = None,
) -> str:
    lines = [
        "Godot Mobile Perf Doctor",
        f"Report schema: 1.1 | Tool: {__version__}",
        f"Profile: {profile} | Texture limit: {max_texture_dimension}px | Viewport budget: {max_viewport_pixels} px",
        f"Findings: {len(findings)}. Textures: {textures.total_textures}. Estimated RGBA memory: {textures.total_estimated_rgba_mb:.2f} MB.",
    ]
    if mobile_ui_metadata:
        lines.append(f"Mobile UI metadata: {mobile_ui_metadata}")
    if adb:
        lines.append(f"ADB: {adb.device or 'unknown'} Android {adb.android or 'unknown'}, {adb.janky_frames}/{adb.total_frames} janky frames.")
    for finding in findings:
        help_text = explain_rule(finding.rule_id)
        lines.append(f"[{finding.severity.upper()}] {help_text['title']}: {finding.message}")
        lines.append(f"  Why it matters: {help_text['explanation']}")
    if not findings:
        lines.append("No findings.")
    return "\n".join(lines)


def render_markdown_report(
    findings: list[Finding],
    textures: TextureSummary,
    adb: AdbSummary | None,
    *,
    profile: str,
    max_texture_dimension: int,
    max_viewport_pixels: int,
    mobile_ui_metadata: str | None = None,
) -> str:
    lines = [
        "# Mobile Performance Report",
        "",
        f"Report schema: `1.1`",
        f"Tool version: `{__version__}`",
        f"Profile: `{profile}`",
        f"Texture dimension limit: `{max_texture_dimension}px`",
        f"Viewport pixel budget: `{max_viewport_pixels}`",
        "",
        f"Textures scanned: {textures.total_textures}",
        f"Estimated RGBA memory: {textures.total_estimated_rgba_mb:.2f} MB",
        "",
        "| Severity | Rule | Message | Why it matters |",
        "|---|---|---|---|",
    ]
    if mobile_ui_metadata:
        lines.insert(7, f"Mobile UI metadata: `{mobile_ui_metadata}`")
    for finding in findings:
        help_text = explain_rule(finding.rule_id)
        lines.append(
            "| "
            f"{finding.severity} | {help_text['title']} | {_markdown_cell(finding.message)} | "
            f"{_markdown_cell(help_text['explanation'])} |"
        )
    if not findings:
        lines.append("| ok | none | No findings. | - |")
    if adb:
        lines.extend(["", f"ADB sample: {adb.device}, Android {adb.android}, {adb.janky_frames}/{adb.total_frames} janky frames."])
    return "\n".join(lines) + "\n"


def render_json_report(
    findings: list[Finding],
    textures: TextureSummary,
    adb: AdbSummary | None,
    *,
    profile: str,
    max_texture_dimension: int,
    max_viewport_pixels: int,
    mobile_ui_metadata: str | None = None,
) -> str:
    payload = {
        "tool": "godot-mobile-perf-doctor",
        "metadata": _metadata(profile, max_texture_dimension, max_viewport_pixels, mobile_ui_metadata),
        "summary": {
            "findings": len(findings),
            "errors": sum(1 for finding in findings if finding.severity == "error"),
            "warnings": sum(1 for finding in findings if finding.severity == "warning"),
            "textures": textures.total_textures,
            "large_textures": len(textures.large_textures),
        },
        "rules": catalog_for({finding.rule_id for finding in findings}),
        "findings": [finding.to_dict() for finding in findings],
        "textures": textures.to_dict(),
        "adb": adb.to_dict() if adb else None,
    }
    return json.dumps(payload, indent=2, sort_keys=True)


def render_sarif_report(
    findings: list[Finding],
    textures: TextureSummary,
    adb: AdbSummary | None,
    *,
    profile: str,
    max_texture_dimension: int,
    max_viewport_pixels: int,
    mobile_ui_metadata: str | None = None,
) -> str:
    rules = {}
    results = []
    for finding in findings:
        help_text = explain_rule(finding.rule_id)
        rules.setdefault(
            finding.rule_id,
            {
                "id": finding.rule_id,
                "name": help_text["title"],
                "shortDescription": {"text": help_text["explanation"]},
                "help": {"text": finding.message},
            },
        )
        results.append(
            {
                "ruleId": finding.rule_id,
                "level": _sarif_level(finding.severity),
                "message": {"text": finding.message},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": (finding.path or "project.godot").replace("\\", "/")}
                        }
                    }
                ],
            }
        )
    payload = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "godot-mobile-perf-doctor",
                        "semanticVersion": __version__,
                        "properties": _metadata(
                            profile, max_texture_dimension, max_viewport_pixels, mobile_ui_metadata
                        ),
                        "rules": list(rules.values()),
                    }
                },
                "results": results,
            }
        ],
    }
    return json.dumps(payload, indent=2, sort_keys=True)


def _metadata(
    profile: str,
    max_texture_dimension: int,
    max_viewport_pixels: int,
    mobile_ui_metadata: str | None = None,
) -> dict[str, object]:
    return {
        "schema_version": "1.1",
        "tool_version": __version__,
        "report_kind": "mobile_performance_scan",
        "profile": profile,
        "profile_description": get_profile(profile).description,
        "limits": {
            "max_texture_dimension": max_texture_dimension,
            "max_viewport_pixels": max_viewport_pixels,
        },
        "mobile_ui_metadata": mobile_ui_metadata,
        "formats": ["text", "json", "markdown", "sarif"],
    }


def _markdown_cell(value: str) -> str:
    return value.replace("|", "\\|")


def _sarif_level(severity: str) -> str:
    if severity == "error":
        return "error"
    if severity == "warning":
        return "warning"
    return "note"
