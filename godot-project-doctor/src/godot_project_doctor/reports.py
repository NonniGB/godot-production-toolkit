from __future__ import annotations

from html import escape
import json


def render_json(summary: dict[str, object]) -> str:
    return json.dumps(summary, indent=2, sort_keys=True)


def render_text(summary: dict[str, object]) -> str:
    totals = summary["summary"]
    lines = [
        "Godot Project Doctor Report",
        f"Tools: {totals['tools']}",
        f"Errors: {totals['errors']}",
        f"Warnings: {totals['warnings']}",
    ]
    for report in summary["reports"]:
        report_summary = report["summary"]
        lines.append(f"- {report['tool']}: {report_summary['errors']} error(s), {report_summary['warnings']} warning(s)")
    return "\n".join(lines)


def render_markdown(summary: dict[str, object]) -> str:
    totals = summary["summary"]
    lines = [
        "# Godot Project Doctor Report",
        "",
        f"- Tools: {totals['tools']}",
        f"- Errors: {totals['errors']}",
        f"- Warnings: {totals['warnings']}",
        "",
        "| Tool | Errors | Warnings | Report |",
        "|---|---:|---:|---|",
    ]
    for report in summary["reports"]:
        report_summary = report["summary"]
        lines.append(
            f"| {report['tool']} | {report_summary['errors']} | {report_summary['warnings']} | {report['path']} |"
        )
    return "\n".join(lines)


def render_html(summary: dict[str, object]) -> str:
    totals = summary["summary"]
    rows = []
    for report in summary["reports"]:
        report_summary = report["summary"]
        rows.append(
            "<tr>"
            f"<td>{escape(str(report['tool']))}</td>"
            f"<td>{report_summary['errors']}</td>"
            f"<td>{report_summary['warnings']}</td>"
            f"<td>{escape(str(report['path']))}</td>"
            "</tr>"
        )
    return "\n".join(
        [
            "<!doctype html>",
            "<html lang=\"en\">",
            "<head>",
            "<meta charset=\"utf-8\">",
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">",
            "<title>Godot Project Doctor Report</title>",
            "<style>",
            "body{font-family:system-ui,-apple-system,Segoe UI,sans-serif;margin:2rem;line-height:1.45;color:#172033}",
            "table{border-collapse:collapse;width:100%;max-width:980px}th,td{border:1px solid #d7dce5;padding:.55rem;text-align:left}",
            "th{background:#f4f6f9}.totals{display:flex;gap:1rem;margin:1rem 0}.totals div{border:1px solid #d7dce5;padding:.75rem}",
            "</style>",
            "</head>",
            "<body>",
            "<h1>Godot Project Doctor Report</h1>",
            "<div class=\"totals\">",
            f"<div><strong>Tools</strong><br>{totals['tools']}</div>",
            f"<div><strong>Errors</strong><br>{totals['errors']}</div>",
            f"<div><strong>Warnings</strong><br>{totals['warnings']}</div>",
            "</div>",
            "<table>",
            "<thead><tr><th>Tool</th><th>Errors</th><th>Warnings</th><th>Report</th></tr></thead>",
            "<tbody>",
            *rows,
            "</tbody>",
            "</table>",
            "</body>",
            "</html>",
        ]
    )


def render_summary(summary: dict[str, object], output_format: str) -> str:
    if output_format == "json":
        return render_json(summary)
    if output_format == "markdown":
        return render_markdown(summary)
    if output_format == "html":
        return render_html(summary)
    return render_text(summary)
