from __future__ import annotations

import json

from .models import AdbSummary, Finding, TextureSummary


def render_text_report(findings: list[Finding], textures: TextureSummary, adb: AdbSummary | None) -> str:
    lines = [
        "Godot Mobile Perf Doctor",
        f"Findings: {len(findings)}. Textures: {textures.total_textures}. Estimated RGBA memory: {textures.total_estimated_rgba_mb:.2f} MB.",
    ]
    if adb:
        lines.append(f"ADB: {adb.device or 'unknown'} Android {adb.android or 'unknown'}, {adb.janky_frames}/{adb.total_frames} janky frames.")
    for finding in findings:
        lines.append(f"[{finding.severity.upper()}] {finding.rule_id}: {finding.message}")
    if not findings:
        lines.append("No findings.")
    return "\n".join(lines)


def render_markdown_report(findings: list[Finding], textures: TextureSummary, adb: AdbSummary | None) -> str:
    lines = [
        "# Mobile Performance Report",
        "",
        f"Textures scanned: {textures.total_textures}",
        f"Estimated RGBA memory: {textures.total_estimated_rgba_mb:.2f} MB",
        "",
        "| Severity | Rule | Message |",
        "|---|---|---|",
    ]
    for finding in findings:
        lines.append(f"| {finding.severity} | {finding.rule_id} | {finding.message} |")
    if not findings:
        lines.append("| ok | none | No findings. |")
    if adb:
        lines.extend(["", f"ADB sample: {adb.device}, Android {adb.android}, {adb.janky_frames}/{adb.total_frames} janky frames."])
    return "\n".join(lines) + "\n"


def render_json_report(findings: list[Finding], textures: TextureSummary, adb: AdbSummary | None) -> str:
    payload = {
        "tool": "godot-mobile-perf-doctor",
        "summary": {
            "findings": len(findings),
            "errors": sum(1 for finding in findings if finding.severity == "error"),
            "warnings": sum(1 for finding in findings if finding.severity == "warning"),
            "textures": textures.total_textures,
            "large_textures": len(textures.large_textures),
        },
        "findings": [finding.to_dict() for finding in findings],
        "textures": textures.to_dict(),
        "adb": adb.to_dict() if adb else None,
    }
    return json.dumps(payload, indent=2, sort_keys=True)


def render_sarif_report(findings: list[Finding], textures: TextureSummary, adb: AdbSummary | None) -> str:
    rules = {}
    results = []
    for finding in findings:
        rules.setdefault(
            finding.rule_id,
            {
                "id": finding.rule_id,
                "name": finding.rule_id,
                "shortDescription": {"text": finding.message},
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
                        "rules": list(rules.values()),
                    }
                },
                "results": results,
            }
        ],
    }
    return json.dumps(payload, indent=2, sort_keys=True)


def _sarif_level(severity: str) -> str:
    if severity == "error":
        return "error"
    if severity == "warning":
        return "warning"
    return "note"
