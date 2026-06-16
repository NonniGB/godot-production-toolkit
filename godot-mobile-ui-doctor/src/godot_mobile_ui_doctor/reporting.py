from __future__ import annotations

import json
from typing import Any


def render_report(report: dict[str, Any], fmt: str) -> str:
    if fmt == "json":
        return json.dumps(report, indent=2, sort_keys=True)
    if report.get("kind") == "mobile_readiness_matrix":
        return _matrix_markdown(report) if fmt == "markdown" else _matrix_text(report)
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
        help_text = f" ({finding['rule_help']})" if finding.get("rule_help") else ""
        lines.append(
            f"- {finding['severity'].upper()} {finding['rule_id']}{location}: "
            f"{finding['message']}{help_text}"
        )
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

    lines.extend(["| Severity | Rule | Location | Message | Help |", "|---|---|---|---|---|"])
    for finding in findings:
        lines.append(
            f"| {finding['severity']} | `{finding['rule_id']}` | "
            f"{_location_text(finding)} | {finding['message']} | {finding.get('rule_help', '')} |"
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


def _matrix_text(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "Godot Mobile UI Readiness Matrix",
        (
            f"Screens: {summary['screens']} | Pass: {summary['ready']} | "
            f"Review: {summary['review']} | Action: {summary['action']}"
        ),
        f"Errors: {summary['errors']} | Warnings: {summary['warnings']}",
        "",
    ]
    for row in report["matrix"]:
        lines.append(
            f"- {row['screen']} / {row['viewport']} ({row['viewport_size']}): "
            f"{row['status']} | safe area {row['safe_area']} | "
            f"touch {row['touch_targets']} | spacing {row['spacing']} | text {row['text_fit']}"
        )
    return "\n".join(lines)


def _matrix_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Godot Mobile UI Readiness Matrix",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Screens | {summary['screens']} |",
        f"| Pass | {summary['ready']} |",
        f"| Review | {summary['review']} |",
        f"| Action needed | {summary['action']} |",
        f"| Errors | {summary['errors']} |",
        f"| Warnings | {summary['warnings']} |",
        "",
        "| Screen | Viewport | Size | Status | Safe Area | Touch Targets | Spacing | Text Fit | Bounds |",
        "|---|---|---:|---|---|---|---|---|---|",
    ]
    for row in report["matrix"]:
        lines.append(
            f"| {row['screen']} | {row['viewport']} | {row['viewport_size']} | "
            f"{row['status']} | {row['safe_area']} | {row['touch_targets']} | "
            f"{row['spacing']} | {row['text_fit']} | {row['viewport_bounds']} |"
        )
    return "\n".join(lines)
