from __future__ import annotations

import json
from typing import Any


def render_report(report: dict[str, Any], fmt: str) -> str:
    if fmt == "json":
        return json.dumps(report, indent=2, sort_keys=True)
    if fmt == "markdown":
        return _markdown(report)
    return _text(report)


def _text(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "Godot Mobile UI Doctor",
        (
            f"Screens: {summary['screens']} | Viewports: {summary['viewports']} | "
            f"Nodes: {summary['nodes']} | Interactive: {summary['interactive_nodes']}"
        ),
        f"Errors: {summary['errors']} | Warnings: {summary['warnings']}",
    ]
    findings = report["findings"]
    if not findings:
        lines.append("No mobile UI findings.")
        return "\n".join(lines)
    lines.append("")
    for finding in findings:
        location = _location(finding)
        lines.append(f"- {finding['severity'].upper()} {finding['rule_id']}{location}: {finding['message']}")
    return "\n".join(lines)


def _markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Godot Mobile UI Doctor",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Screens | {summary['screens']} |",
        f"| Viewports | {summary['viewports']} |",
        f"| Nodes | {summary['nodes']} |",
        f"| Interactive nodes | {summary['interactive_nodes']} |",
        f"| Errors | {summary['errors']} |",
        f"| Warnings | {summary['warnings']} |",
        "",
        "## Findings",
        "",
    ]
    findings = report["findings"]
    if not findings:
        lines.append("No mobile UI findings.")
        return "\n".join(lines)

    lines.extend(["| Severity | Rule | Location | Message |", "|---|---|---|---|"])
    for finding in findings:
        lines.append(
            f"| {finding['severity']} | `{finding['rule_id']}` | "
            f"{_location_text(finding)} | {finding['message']} |"
        )
    return "\n".join(lines)


def _location(finding: dict[str, Any]) -> str:
    text = _location_text(finding)
    return f" [{text}]" if text else ""


def _location_text(finding: dict[str, Any]) -> str:
    parts = []
    for key in ("screen", "viewport", "node"):
        if finding.get(key):
            parts.append(str(finding[key]))
    return " / ".join(parts)
