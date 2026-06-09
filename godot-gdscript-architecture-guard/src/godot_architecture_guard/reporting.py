from __future__ import annotations

import json
from typing import Any


def render_report(report: dict[str, Any], output_format: str) -> str:
    if output_format == "json":
        return json.dumps(report, indent=2, sort_keys=True)
    if output_format == "sarif":
        return _sarif(report)
    if output_format == "markdown":
        return _markdown(report)
    return _text(report)


def _text(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "Godot GDScript Architecture Guard",
        f"Scanned {summary['scripts']} script(s), {summary['modules']} module(s): {summary['errors']} error(s), {summary['warnings']} warning(s).",
    ]
    for finding in report["findings"]:
        lines.append(f"[{finding['severity'].upper()}] {finding['rule_id']} - {finding.get('path', '')}: {finding['message']}")
    if not report["findings"]:
        lines.append("No findings.")
    return "\n".join(lines)


def _markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Godot GDScript Architecture Guard",
        "",
        f"- Scripts: {summary['scripts']}",
        f"- Modules: {summary['modules']}",
        f"- Dependencies: {summary['dependencies']}",
        f"- Errors: {summary['errors']}",
        f"- Warnings: {summary['warnings']}",
        "",
        "| Severity | Rule | Path | Message |",
        "|---|---|---|---|",
    ]
    if report["findings"]:
        for finding in report["findings"]:
            lines.append(f"| {finding['severity']} | {finding['rule_id']} | {finding.get('path', '')} | {finding['message']} |")
    else:
        lines.append("| info | clean |  | No findings. |")
    return "\n".join(lines)


def _sarif(report: dict[str, Any]) -> str:
    rules = sorted({finding["rule_id"] for finding in report["findings"]})
    payload = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "godot-gdscript-architecture-guard",
                        "informationUri": "https://github.com/NonniGB/godot-production-toolkit/tree/main/godot-gdscript-architecture-guard",
                        "rules": [
                            {"id": rule, "name": rule, "shortDescription": {"text": rule.replace("_", " ")}}
                            for rule in rules
                        ],
                    }
                },
                "results": [_finding_to_sarif(finding) for finding in report["findings"]],
            }
        ],
    }
    return json.dumps(payload, indent=2, sort_keys=True)


def _finding_to_sarif(finding: dict[str, Any]) -> dict[str, Any]:
    return {
        "ruleId": finding["rule_id"],
        "level": "error" if finding["severity"] == "error" else "warning",
        "message": {"text": finding["message"]},
        "locations": [
            {
                "physicalLocation": {
                    "artifactLocation": {"uri": finding.get("path", "project.godot")},
                }
            }
        ],
    }

