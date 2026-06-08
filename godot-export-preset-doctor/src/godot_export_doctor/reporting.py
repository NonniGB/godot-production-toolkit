from __future__ import annotations

import json

from .models import ExportPreset, Finding


def render_text_report(presets: list[ExportPreset], findings: list[Finding]) -> str:
    preset_word = "export preset" if len(presets) == 1 else "export presets"
    errors = sum(1 for finding in findings if finding.severity == "error")
    warnings = sum(1 for finding in findings if finding.severity == "warning")
    lines = [
        "Godot Export Preset Doctor",
        f"Scanned {len(presets)} {preset_word}: {errors} error(s), {warnings} warning(s).",
    ]
    if not findings:
        lines.append("No findings.")
        return "\n".join(lines)

    for finding in findings:
        target = finding.preset_name
        if finding.preset_index is not None:
            target = f"preset.{finding.preset_index} ({finding.preset_name})"
        lines.append(f"[{finding.severity.upper()}] {finding.rule_id} - {target}: {finding.message}")
    return "\n".join(lines)


def render_json_report(presets: list[ExportPreset], findings: list[Finding]) -> str:
    payload = {
        "tool": "godot-export-preset-doctor",
        "summary": {
            "presets": len(presets),
            "findings": len(findings),
            "errors": sum(1 for finding in findings if finding.severity == "error"),
            "warnings": sum(1 for finding in findings if finding.severity == "warning"),
        },
        "presets": [preset.to_dict() for preset in presets],
        "findings": [finding.to_dict() for finding in findings],
    }
    return json.dumps(payload, indent=2, sort_keys=True)


def render_sarif_report(findings: list[Finding]) -> str:
    rules = sorted({finding.rule_id for finding in findings})
    payload = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "godot-export-preset-doctor",
                        "informationUri": "https://github.com/example/godot-export-preset-doctor",
                        "rules": [
                            {
                                "id": rule,
                                "name": rule,
                                "shortDescription": {"text": rule.replace("_", " ")},
                            }
                            for rule in rules
                        ],
                    }
                },
                "results": [_finding_to_sarif(finding) for finding in findings],
            }
        ],
    }
    return json.dumps(payload, indent=2, sort_keys=True)


def _finding_to_sarif(finding: Finding) -> dict[str, object]:
    result: dict[str, object] = {
        "ruleId": finding.rule_id,
        "level": _sarif_level(finding.severity),
        "message": {"text": finding.message},
        "locations": [
            {
                "physicalLocation": {
                    "artifactLocation": {"uri": "export_presets.cfg"},
                }
            }
        ],
    }
    if finding.preset_index is not None:
        result["properties"] = {
            "preset_index": finding.preset_index,
            "preset_name": finding.preset_name,
            "option": finding.option,
        }
    return result


def _sarif_level(severity: str) -> str:
    if severity == "error":
        return "error"
    if severity == "warning":
        return "warning"
    return "note"
