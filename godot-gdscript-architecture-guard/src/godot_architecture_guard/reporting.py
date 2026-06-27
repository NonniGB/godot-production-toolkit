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
    if report.get("hotspots"):
        lines.append("Hotspots:")
        for row in report["hotspots"][:5]:
            lines.append(
                f"  {row['path']} score={row['score']} incoming={row['incoming']} "
                f"outgoing={row['outgoing']} autoload_refs={row['autoload_references']}"
            )
    if report.get("possible_unused_scripts"):
        lines.append("Possible unused scripts:")
        for row in report["possible_unused_scripts"][:5]:
            lines.append(f"  {row['path']} ({row.get('module') or 'unowned'})")
    if report.get("possible_unused_resources"):
        lines.append("Possible unused resources:")
        for row in report["possible_unused_resources"][:5]:
            lines.append(f"  {row['path']} ({row.get('module') or 'unowned'})")
    if report.get("owner_summaries"):
        lines.append("Module ownership:")
        for row in report["owner_summaries"]:
            lines.append(
                f"  {row['module']}: scripts={row['matched_scripts']} "
                f"incoming={row['incoming_dependencies']} outgoing={row['outgoing_dependencies']}"
            )
    for finding in report["findings"]:
        title = finding.get("title", finding["rule_id"])
        lines.append(
            f"[{finding['severity'].upper()}] {finding['rule_id']} - {title} - "
            f"{finding.get('path', '')}: {finding['message']}"
        )
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
        f"- Owner summaries: {summary.get('owner_summaries', 0)}",
        f"- Hotspots: {summary.get('hotspots', 0)}",
        f"- Possible unused scripts: {summary.get('possible_unused_scripts', 0)}",
        f"- Possible unused resources: {summary.get('possible_unused_resources', 0)}",
        f"- Errors: {summary['errors']}",
        f"- Warnings: {summary['warnings']}",
        "",
        "| Severity | Rule | Path | Message | Suggestion |",
        "|---|---|---|---|---|",
    ]
    if report["findings"]:
        for finding in report["findings"]:
            lines.append(
                f"| {finding['severity']} | {finding['rule_id']} | {finding.get('path', '')} | "
                f"{finding['message']} | {finding.get('suggestion', '')} |"
            )
    else:
        lines.append("| info | clean |  | No findings. | |")
    lines.extend(_markdown_owner_summaries(report))
    lines.extend(_markdown_dependency_graph(report))
    lines.extend(_markdown_hotspots(report))
    lines.extend(_markdown_possible_unused_scripts(report))
    lines.extend(_markdown_possible_unused_resources(report))
    return "\n".join(lines)


def _markdown_owner_summaries(report: dict[str, Any]) -> list[str]:
    rows = report.get("owner_summaries", [])
    if not rows:
        return ["", "## Module Ownership Summary", "", "No configured modules found."]
    lines = [
        "",
        "## Module Ownership Summary",
        "",
        "| Module | Scripts | In | Out | Autoload refs | Boundary violations | "
        "Autoload violations | Unmatched paths | Hotspots | Possible unused |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['module']} | {row['matched_scripts']} | "
            f"{row['incoming_dependencies']} | {row['outgoing_dependencies']} | "
            f"{row['autoload_references']} | {row['boundary_violations']} | "
            f"{row['autoload_violations']} | {row['unmatched_path_patterns']} | "
            f"{row['hotspots']} | {row['possible_unused_scripts']} |"
        )
    return lines


def _markdown_dependency_graph(report: dict[str, Any]) -> list[str]:
    dependencies = report.get("dependencies", [])
    if not dependencies:
        return ["", "## Module Dependency Graph", "", "No module dependencies found."]
    modules = sorted(report.get("modules", {}))
    lines = ["", "## Module Dependency Graph", "", "```mermaid", "flowchart LR"]
    for name in modules:
        lines.append(f"  {name}[{name}]")
    for edge in dependencies:
        lines.append(f"  {edge['source']} --> {edge['target']}")
    lines.append("```")
    return lines


def _markdown_hotspots(report: dict[str, Any]) -> list[str]:
    rows = report.get("hotspots", [])
    if not rows:
        return ["", "## Dependency Hotspots", "", "No dependency hotspots found."]
    lines = [
        "",
        "## Dependency Hotspots",
        "",
        "| Score | Path | Module | Incoming | Outgoing | Autoload refs |",
        "|---:|---|---|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['score']} | {row['path']} | {row.get('module') or ''} | "
            f"{row['incoming']} | {row['outgoing']} | {row['autoload_references']} |"
        )
    return lines


def _markdown_possible_unused_scripts(report: dict[str, Any]) -> list[str]:
    rows = report.get("possible_unused_scripts", [])
    if not rows:
        return ["", "## Possible Unused Scripts", "", "No possible unused scripts found."]
    lines = [
        "",
        "## Possible Unused Scripts",
        "",
        "| Path | Module | Reason |",
        "|---|---|---|",
    ]
    for row in rows:
        lines.append(f"| {row['path']} | {row.get('module') or ''} | {row['reason']} |")
    return lines


def _markdown_possible_unused_resources(report: dict[str, Any]) -> list[str]:
    rows = report.get("possible_unused_resources", [])
    if not rows:
        return ["", "## Possible Unused Resources", "", "No possible unused resources found."]
    lines = [
        "",
        "## Possible Unused Resources",
        "",
        "| Path | Module | Reason |",
        "|---|---|---|",
    ]
    for row in rows:
        lines.append(f"| {row['path']} | {row.get('module') or ''} | {row['reason']} |")
    return lines


def _sarif(report: dict[str, Any]) -> str:
    rule_help = report.get("rule_help", {})
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
                            _sarif_rule(rule, rule_help.get(rule, {}))
                            for rule in rules
                        ],
                    }
                },
                "results": [_finding_to_sarif(finding) for finding in report["findings"]],
            }
        ],
    }
    return json.dumps(payload, indent=2, sort_keys=True)


def _sarif_rule(rule: str, help_text: dict[str, str]) -> dict[str, Any]:
    title = help_text.get("title", rule.replace("_", " "))
    return {
        "id": rule,
        "name": title,
        "shortDescription": {"text": title},
        "fullDescription": {"text": help_text.get("explanation", title)},
        "help": {"text": help_text.get("suggestion", "")},
    }


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
