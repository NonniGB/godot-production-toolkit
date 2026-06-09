from __future__ import annotations

import json

from . import __version__
from .coverage import build_summary
from .models import ApiItem, ThresholdFinding
from .rule_help import catalog_for, explain_threshold


def render_markdown_index(items: list[ApiItem], *, title: str = "GDScript API Index") -> str:
    lines = [
        f"# {title}",
        "",
        "| Kind | Name | Location | Documented |",
        "|---|---|---:|:---:|",
    ]
    for item in items:
        documented = "yes" if item.documented else "no"
        lines.append(
            f"| {_markdown_cell(item.kind)} | {_markdown_cell(item.name)} | "
            f"{_markdown_cell(f'{item.path}:{item.line}')} | {documented} |"
        )
    if not items:
        lines.append("| none | none | none | yes |")
    lines.append("")
    return "\n".join(lines)


def render_text_report(items: list[ApiItem], findings: list[ThresholdFinding]) -> str:
    summary = build_summary(items)
    lines = ["GDScript API Comment Coverage"]
    for kind, row in summary.items():
        lines.append(
            f"{kind}: {row['documented']}/{row['total']} documented ({row['coverage']:.2f}%)."
        )
    if findings:
        for finding in findings:
            help_text = explain_threshold(finding.kind)
            lines.append(f"[{finding.severity.upper()}] {help_text['title']}: {finding.message}")
            lines.append(f"  Why it matters: {help_text['explanation']}")
    else:
        lines.append("No threshold failures.")
    return "\n".join(lines)


def render_json_report(items: list[ApiItem], findings: list[ThresholdFinding]) -> str:
    payload = {
        "tool": "gdscript-api-comment-coverage",
        "metadata": {
            "schema_version": "1.1",
            "tool_version": __version__,
            "report_kind": "gdscript_api_comment_coverage",
            "formats": ["text", "json", "markdown"],
        },
        "summary": build_summary(items),
        "rules": catalog_for({finding.kind for finding in findings}),
        "items": [item.to_dict() for item in items],
        "findings": [finding.to_dict() for finding in findings],
    }
    return json.dumps(payload, indent=2, sort_keys=True)


def _markdown_cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")
