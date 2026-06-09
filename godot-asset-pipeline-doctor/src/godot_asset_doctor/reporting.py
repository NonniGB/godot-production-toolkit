from __future__ import annotations

import json

from godot_asset_doctor.models import ScanReport
from godot_asset_doctor.rule_help import explain_issue_code


def report_to_json(report: ScanReport) -> str:
    return json.dumps(report.to_dict(), indent=2, sort_keys=True)


def report_to_sarif(report: ScanReport) -> str:
    rules = {}
    results = []
    for issue in report.issues:
        help_text = explain_issue_code(issue.code)
        rules.setdefault(
            issue.code,
            {
                "id": issue.code,
                "name": help_text["title"],
                "shortDescription": {"text": help_text["explanation"]},
                "help": {"text": issue.suggestion},
            },
        )
        results.append(
            {
                "ruleId": issue.code,
                "level": _sarif_level(issue.severity),
                "message": {"text": issue.message},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": str(issue.path).replace("\\", "/")}
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
                        "name": "godot-asset-pipeline-doctor",
                        "rules": list(rules.values()),
                    }
                },
                "results": results,
            }
        ],
    }
    return json.dumps(payload, indent=2, sort_keys=True)


def report_to_text(report: ScanReport) -> str:
    summary = report.summary()
    payload = report.to_dict()
    metadata = payload["metadata"]
    lines = [
        "Godot Asset Pipeline Doctor",
        f"Report schema: {metadata['schema_version']} | Tool: {metadata['tool_version']}",
        f"Root: {summary['root']}",
        f"Profile: {summary['profile']}",
        (
            f"Assets: {summary['asset_count']} | Issues: {summary['issue_count']} | "
            f"Errors: {summary['error_count']} | Warnings: {summary['warning_count']}"
        ),
    ]

    if not report.issues:
        lines.append("No issues found.")
        return "\n".join(lines)

    lines.append("")
    for issue in report.issues:
        help_text = explain_issue_code(issue.code)
        lines.append(f"[{issue.severity.upper()}] {help_text['title']}: {issue.path}")
        lines.append(f"  {issue.message}")
        lines.append(f"  Why it matters: {help_text['explanation']}")
        lines.append(f"  Suggestion: {issue.suggestion}")

    return "\n".join(lines)


def _sarif_level(severity: str) -> str:
    if severity == "error":
        return "error"
    if severity == "warning":
        return "warning"
    return "note"
