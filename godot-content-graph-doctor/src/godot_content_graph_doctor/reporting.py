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
    lines = [
        "Godot Content Graph Doctor",
        (
            f"Scanned {summary['collections']} collection(s), {summary['records']} record(s): "
            f"{summary['errors']} error(s), {summary['warnings']} warning(s)."
        ),
    ]
    if not report["findings"]:
        lines.append("No findings.")
        return "\n".join(lines)
    for finding in report["findings"]:
        target = finding.get("collection", "content")
        if finding.get("item_id"):
            target = f"{target}.{finding['item_id']}"
        lines.append(f"[{finding['severity'].upper()}] {finding['rule_id']} - {target}: {finding['message']}")
    return "\n".join(lines)


def _markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Godot Content Graph Doctor",
        "",
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
        lines.extend(["", "## Findings", "", "| Severity | Rule | Target | Message |", "|---|---|---|---|"])
        for finding in report["findings"]:
            target = finding.get("collection", "")
            if finding.get("item_id"):
                target = f"{target}.{finding['item_id']}"
            lines.append(
                f"| {finding['severity']} | {finding['rule_id']} | {target} | {finding['message']} |"
            )
    return "\n".join(lines)

