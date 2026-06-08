from __future__ import annotations

import json

from .models import CsvTable, Finding, PoCatalog

Catalog = CsvTable | PoCatalog


def render_text_report(catalogs: list[Catalog], findings: list[Finding]) -> str:
    lines = [
        "Godot Localization QA Guard",
        f"Scanned {len(catalogs)} catalog(s): {len(findings)} finding(s).",
    ]
    for finding in findings:
        lines.append(f"[{finding.severity.upper()}] {finding.rule_id} {finding.key or '-'}: {finding.message}")
    if not findings:
        lines.append("No findings.")
    return "\n".join(lines)


def render_markdown_report(catalogs: list[Catalog], findings: list[Finding]) -> str:
    lines = [
        "# Localization QA Report",
        "",
        f"Catalogs scanned: {len(catalogs)}",
        "",
        "| Severity | Rule | Key | Message | Location |",
        "|---|---|---|---|---|",
    ]
    for finding in findings:
        location = finding.path or ""
        if finding.line:
            location = f"{location}:{finding.line}"
        lines.append(
            f"| {finding.severity} | {finding.rule_id} | {finding.key or ''} | {finding.message} | {location} |"
        )
    if not findings:
        lines.append("| ok | none |  | No findings. |  |")
    lines.append("")
    return "\n".join(lines)


def render_json_report(catalogs: list[Catalog], findings: list[Finding]) -> str:
    payload = {
        "tool": "godot-localization-qa-guard",
        "summary": {
            "catalogs": len(catalogs),
            "findings": len(findings),
            "errors": sum(1 for finding in findings if finding.severity == "error"),
            "warnings": sum(1 for finding in findings if finding.severity == "warning"),
        },
        "catalogs": [catalog.to_dict() for catalog in catalogs],
        "findings": [finding.to_dict() for finding in findings],
    }
    return json.dumps(payload, indent=2, sort_keys=True)


def render_sarif_report(catalogs: list[Catalog], findings: list[Finding]) -> str:
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
        physical_location = {
            "artifactLocation": {"uri": (finding.path or "translations").replace("\\", "/")}
        }
        if finding.line:
            physical_location["region"] = {"startLine": finding.line}
        location = {"physicalLocation": physical_location}
        if finding.key:
            location["logicalLocations"] = [{"name": finding.key}]
        results.append(
            {
                "ruleId": finding.rule_id,
                "level": _sarif_level(finding.severity),
                "message": {"text": finding.message},
                "locations": [location],
            }
        )
    payload = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "godot-localization-qa-guard",
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
