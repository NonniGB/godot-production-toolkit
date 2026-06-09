from __future__ import annotations

import json

from . import __version__
from .models import CsvTable, Finding, PoCatalog
from .rule_help import catalog_for, explain_rule

Catalog = CsvTable | PoCatalog


def render_text_report(catalogs: list[Catalog], findings: list[Finding]) -> str:
    lines = [
        "Godot Localization QA Guard",
        f"Scanned {len(catalogs)} catalog(s): {len(findings)} finding(s).",
    ]
    for finding in findings:
        help_text = explain_rule(finding.rule_id)
        lines.append(f"[{finding.severity.upper()}] {help_text['title']} {finding.key or '-'}: {finding.message}")
        lines.append(f"  Why it matters: {help_text['explanation']}")
    if not findings:
        lines.append("No findings.")
    return "\n".join(lines)


def render_markdown_report(catalogs: list[Catalog], findings: list[Finding]) -> str:
    lines = [
        "# Localization QA Report",
        "",
        f"Catalogs scanned: {len(catalogs)}",
        "",
        "| Severity | Rule | Key | Message | Why It Matters | Location |",
        "|---|---|---|---|---|---|",
    ]
    for finding in findings:
        location = finding.path or ""
        if finding.line:
            location = f"{location}:{finding.line}"
        help_text = explain_rule(finding.rule_id)
        lines.append(
            f"| {finding.severity} | {finding.rule_id} | {finding.key or ''} | "
            f"{finding.message} | {help_text['explanation']} | {location} |"
        )
    if not findings:
        lines.append("| ok | none |  | No findings. |  |  |")
    lines.append("")
    return "\n".join(lines)


def render_json_report(catalogs: list[Catalog], findings: list[Finding]) -> str:
    payload = {
        "tool": "godot-localization-qa-guard",
        "metadata": {
            "schema_version": "1.1",
            "tool_version": __version__,
            "report_kind": "localization_qa",
            "formats": ["text", "json", "markdown", "sarif"],
        },
        "summary": {
            "catalogs": len(catalogs),
            "findings": len(findings),
            "errors": sum(1 for finding in findings if finding.severity == "error"),
            "warnings": sum(1 for finding in findings if finding.severity == "warning"),
        },
        "catalogs": [catalog.to_dict() for catalog in catalogs],
        "rules": catalog_for({finding.rule_id for finding in findings}),
        "findings": [finding.to_dict() for finding in findings],
    }
    return json.dumps(payload, indent=2, sort_keys=True)


def render_sarif_report(catalogs: list[Catalog], findings: list[Finding]) -> str:
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
