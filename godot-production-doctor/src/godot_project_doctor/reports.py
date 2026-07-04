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
        lines.append(f"  Source report: {report.get('source_report_path', report['path'])}")
        reproduction = report.get("reproduction", {})
        if isinstance(reproduction, dict) and reproduction.get("command"):
            lines.append(f"  Reproduce: {reproduction['command']}")
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
        "| Tool | Errors | Warnings | Source Report | Reproduce |",
        "|---|---:|---:|---|---|",
    ]
    for report in summary["reports"]:
        report_summary = report["summary"]
        reproduction = report.get("reproduction", {})
        reproduce_command = ""
        if isinstance(reproduction, dict):
            reproduce_command = str(reproduction.get("command", ""))
        lines.append(
            f"| {report['tool']} | {report_summary['errors']} | {report_summary['warnings']} | "
            f"{report.get('source_report_path', report['path'])} | {reproduce_command or 'n/a'} |"
        )
    return "\n".join(lines)


def render_html(summary: dict[str, object]) -> str:
    totals = summary["summary"]
    rows = []
    for report in summary["reports"]:
        report_summary = report["summary"]
        status_class = "clean"
        status_label = "Clean"
        if int(report_summary["errors"]) > 0:
            status_class = "error"
            status_label = "Action needed"
        elif int(report_summary["warnings"]) > 0:
            status_class = "warning"
            status_label = "Review"
        rows.append(
            "<tr>"
            f"<td><span class=\"status {status_class}\">{status_label}</span></td>"
            f"<td>{escape(str(report['tool']))}</td>"
            f"<td>{report_summary['errors']}</td>"
            f"<td>{report_summary['warnings']}</td>"
            f"<td>{escape(str(report.get('source_report_path', report['path'])))}</td>"
            f"<td>{escape(_reproduction_command(report))}</td>"
            "</tr>"
        )
    issue_cards = []
    for report in summary["reports"]:
        for finding in report.get("findings", [])[:3]:
            severity = escape(str(finding.get("severity", "info")))
            title = escape(str(finding.get("rule_id") or finding.get("code") or finding.get("id") or "finding"))
            message = escape(str(finding.get("message", "")))
            tool = escape(str(report["tool"]))
            source = escape(str(report.get("source_report_path", report["path"])))
            reproduce = escape(_reproduction_command(report))
            card = (
                "<article class=\"finding\">"
                f"<span class=\"finding-severity\">{severity}</span>"
                f"<h3>{title}</h3>"
                f"<p>{message}</p>"
                f"<small>{tool} - source: {source}</small>"
            )
            if reproduce != "n/a":
                card += f"<pre>{reproduce}</pre>"
            card += "</article>"
            issue_cards.append(card)
    return "\n".join(
        [
            "<!doctype html>",
            "<html lang=\"en\">",
            "<head>",
            "<meta charset=\"utf-8\">",
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">",
            "<title>Godot Project Doctor Report</title>",
            "<style>",
            ":root{color-scheme:light;--ink:#172033;--muted:#667085;--line:#d7dce5;--bg:#f7f8fb;--panel:#fff;--accent:#2563eb;--ok:#047857;--warn:#b45309;--err:#b42318}",
            "*{box-sizing:border-box}body{font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,sans-serif;margin:0;line-height:1.45;color:var(--ink);background:var(--bg)}",
            "main{max-width:1120px;margin:0 auto;padding:40px 28px}.eyebrow{color:var(--accent);font-size:.78rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em}",
            "h1{margin:.25rem 0 .35rem;font-size:2.2rem;line-height:1.08}p.lead{margin:0 0 1.4rem;color:var(--muted);max-width:760px}",
            ".totals{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin:24px 0}.metric{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:16px;box-shadow:0 8px 24px rgba(23,32,51,.06)}",
            ".metric strong{display:block;color:var(--muted);font-size:.84rem}.metric span{font-size:2rem;font-weight:800}",
            "section{margin-top:28px}table{border-collapse:separate;border-spacing:0;width:100%;background:var(--panel);border:1px solid var(--line);border-radius:8px;overflow:hidden;box-shadow:0 8px 24px rgba(23,32,51,.06)}",
            "th,td{border-bottom:1px solid var(--line);padding:.72rem;text-align:left;vertical-align:top}tr:last-child td{border-bottom:0}th{background:#eef2f7;color:#344054;font-size:.84rem}",
            ".status{display:inline-block;border-radius:999px;padding:.2rem .55rem;font-size:.78rem;font-weight:700}.status.clean{background:#ecfdf3;color:var(--ok)}.status.warning{background:#fffaeb;color:var(--warn)}.status.error{background:#fef3f2;color:var(--err)}",
            ".findings{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:14px}.finding{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:14px;box-shadow:0 8px 24px rgba(23,32,51,.05)}",
            ".finding h3{margin:.25rem 0;font-size:1rem}.finding p{margin:.25rem 0 .5rem;color:var(--muted)}.finding-severity{font-size:.75rem;font-weight:800;text-transform:uppercase;color:var(--err)}small{color:var(--muted)}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f2f4f7;border-radius:6px;padding:.55rem;font-size:.78rem}",
            "@media(max-width:720px){main{padding:28px 16px}.totals{grid-template-columns:1fr}h1{font-size:1.7rem}table{font-size:.88rem}}",
            "</style>",
            "</head>",
            "<body>",
            "<main>",
            "<div class=\"eyebrow\">Godot release evidence</div>",
            "<h1>Godot Project Doctor Report</h1>",
            "<p class=\"lead\">A compact maintainer review summary for export presets, assets, input maps, localization, scene wiring, and mobile performance evidence.</p>",
            "<div class=\"totals\">",
            f"<div class=\"metric\"><strong>Tools checked</strong><span>{totals['tools']}</span></div>",
            f"<div class=\"metric\"><strong>Errors</strong><span>{totals['errors']}</span></div>",
            f"<div class=\"metric\"><strong>Warnings</strong><span>{totals['warnings']}</span></div>",
            "</div>",
            "<section>",
            "<h2>Check Results</h2>",
            "<table>",
            "<thead><tr><th>Status</th><th>Tool</th><th>Errors</th><th>Warnings</th><th>Source Report</th><th>Reproduce</th></tr></thead>",
            "<tbody>",
            *rows,
            "</tbody>",
            "</table>",
            "</section>",
            "<section>",
            "<h2>Top Findings</h2>",
            "<div class=\"findings\">",
            *(issue_cards or ["<p>No findings were present in the summarized JSON reports.</p>"]),
            "</div>",
            "</section>",
            "</main>",
            "</body>",
            "</html>",
        ]
    )


def _reproduction_command(report: dict[str, object]) -> str:
    reproduction = report.get("reproduction", {})
    if isinstance(reproduction, dict) and reproduction.get("command"):
        return str(reproduction["command"])
    return "n/a"


def render_summary(summary: dict[str, object], output_format: str) -> str:
    if output_format == "json":
        return render_json(summary)
    if output_format == "markdown":
        return render_markdown(summary)
    if output_format == "html":
        return render_html(summary)
    return render_text(summary)
