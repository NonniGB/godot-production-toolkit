from __future__ import annotations

import json

from .coverage import build_summary
from .models import ApiItem, ThresholdFinding


def render_markdown_index(items: list[ApiItem], *, title: str = "GDScript API Index") -> str:
    lines = [
        f"# {title}",
        "",
        "| Kind | Name | Location | Documented |",
        "|---|---|---:|:---:|",
    ]
    for item in items:
        documented = "yes" if item.documented else "no"
        lines.append(f"| {item.kind} | {item.name} | {item.path}:{item.line} | {documented} |")
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
            lines.append(f"[{finding.severity.upper()}] {finding.message}")
    else:
        lines.append("No threshold failures.")
    return "\n".join(lines)


def render_json_report(items: list[ApiItem], findings: list[ThresholdFinding]) -> str:
    payload = {
        "tool": "gdscript-api-comment-coverage",
        "summary": build_summary(items),
        "items": [item.to_dict() for item in items],
        "findings": [finding.to_dict() for finding in findings],
    }
    return json.dumps(payload, indent=2, sort_keys=True)
