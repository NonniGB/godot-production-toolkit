from __future__ import annotations

import json

from godot_asset_doctor.models import ScanReport


def report_to_json(report: ScanReport) -> str:
    return json.dumps(report.to_dict(), indent=2, sort_keys=True)


def report_to_sarif(report: ScanReport) -> str:
    rules = {}
    results = []
    for issue in report.issues:
        rules.setdefault(
            issue.code,
            {
                "id": issue.code,
                "name": issue.code,
                "shortDescription": {"text": issue.message},
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
    lines = [
        "Godot Asset Pipeline Doctor",
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
        lines.append(f"[{issue.severity.upper()}] {issue.code}: {issue.path}")
        lines.append(f"  {issue.message}")
        lines.append(f"  Suggestion: {issue.suggestion}")

    return "\n".join(lines)


def _sarif_level(severity: str) -> str:
    if severity == "error":
        return "error"
    if severity == "warning":
        return "warning"
    return "note"
