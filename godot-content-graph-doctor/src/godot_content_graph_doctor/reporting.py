from __future__ import annotations

from html import escape
import json
from typing import Any


def render_report(report: dict[str, Any], output_format: str) -> str:
    if output_format == "json":
        return json.dumps(report, indent=2, sort_keys=True)
    if output_format == "markdown":
        return _markdown(report)
    if output_format == "text":
        return _text(report)
    raise ValueError(f"unsupported output format {output_format!r}")


def _text(report: dict[str, Any]) -> str:
    summary = report["summary"]
    metadata = report.get("metadata", {})
    lines = [
        "Godot Content Graph Doctor",
        f"Report schema: {metadata.get('schema_version', 'unknown')} | Tool: {metadata.get('tool_version', 'unknown')}",
        (
            f"Scanned {summary['collections']} collection(s), {summary['records']} record(s): "
            f"{summary['errors']} error(s), {summary['warnings']} warning(s)."
        ),
    ]
    if not report["findings"]:
        lines.append("No findings.")
    else:
        for finding in report["findings"]:
            target = finding.get("collection", "content")
            if finding.get("item_id"):
                target = f"{target}.{finding['item_id']}"
            lines.append(
                f"[{finding['severity'].upper()}] {finding.get('title', finding['rule_id'])} - "
                f"{target}: {finding['message']}"
            )
            if finding.get("suggestion"):
                lines.append(f"  Try: {finding['suggestion']}")
    if report.get("impact"):
        impact = report["impact"]
        lines.extend(
            [
                "",
                "Changed-file impact:",
                f"- Direct collections: {_join_or_none(impact['direct_collections'])}",
                f"- Downstream collections: {_join_or_none(impact['downstream_collections'])}",
                f"- Unmatched files: {_join_or_none(impact['unmatched_files'])}",
            ]
        )
    return "\n".join(lines)


def _markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    metadata = report.get("metadata", {})
    lines = [
        "# Godot Content Graph Doctor",
        "",
        f"- Report schema: {metadata.get('schema_version', 'unknown')}",
        f"- Tool version: {metadata.get('tool_version', 'unknown')}",
        f"- Collections: {summary['collections']}",
        f"- Records: {summary['records']}",
        f"- Errors: {summary['errors']}",
        f"- Warnings: {summary['warnings']}",
        "",
        "| Collection | Records | Unique IDs | References |",
        "|---|---:|---:|---:|",
    ]
    for name, collection in report["collections"].items():
        lines.append(
            f"| {escape(str(name))} | {collection['records']} | {collection['unique_ids']} | {len(collection['references'])} |"
        )
    if report["findings"]:
        lines.extend(["", "## Findings", "", "| Severity | Rule | Target | Message | Suggested fix |", "|---|---|---|---|---|"])
        for finding in report["findings"]:
            target = finding.get("collection", "")
            if finding.get("item_id"):
                target = f"{target}.{finding['item_id']}"
            lines.append(
                f"| {finding['severity']} | {finding.get('title', finding['rule_id'])} | {target} | "
                f"{finding['message']} | {finding.get('suggestion', '')} |"
            )
        lines.extend(["", "## Rule Notes", "", "| Rule | What it means |", "|---|---|"])
        for rule_id, rule in report.get("rules", {}).items():
            lines.append(f"| {rule.get('title', rule_id)} | {rule.get('explanation', '')} |")
    if report.get("impact"):
        impact = report["impact"]
        lines.extend(
            [
                "",
                "## Changed-File Impact",
                "",
                f"- Direct collections: {_join_or_none(impact['direct_collections'])}",
                f"- Downstream collections: {_join_or_none(impact['downstream_collections'])}",
                f"- Unmatched files: {_join_or_none(impact['unmatched_files'])}",
            ]
        )
    return "\n".join(lines)


def _join_or_none(values: list[str]) -> str:
    return ", ".join(values) if values else "none"
