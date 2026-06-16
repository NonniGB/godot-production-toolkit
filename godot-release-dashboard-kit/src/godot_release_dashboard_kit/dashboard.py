from __future__ import annotations

from html import escape
import json
from pathlib import Path
from typing import Any

from . import __version__


def build_dashboard(reports_dir: Path, title: str = "Godot Release Dashboard") -> dict[str, Any]:
    reports = [_report_card(path) for path in sorted(reports_dir.rglob("*")) if path.suffix.lower() in {".json", ".md"}]
    summary = {
        "reports": len(reports),
        "errors": sum(int(report.get("errors", 0)) for report in reports),
        "warnings": sum(int(report.get("warnings", 0)) for report in reports),
    }
    return {
        "tool": "godot-release-dashboard-kit",
        "tool_version": __version__,
        "schema_version": "1.0",
        "kind": "release_dashboard",
        "title": title,
        "summary": summary,
        "reports": reports,
    }


def render_html(dashboard: dict[str, Any]) -> str:
    cards = "\n".join(_card(report) for report in dashboard["reports"])
    summary = dashboard["summary"]
    return "\n".join(
        [
            "<!doctype html>",
            "<html lang=\"en\"><head><meta charset=\"utf-8\">",
            f"<title>{escape(str(dashboard['title']))}</title>",
            "<style>body{font-family:system-ui,sans-serif;margin:2rem;color:#172033;background:#f7f8fb}.metrics{display:flex;gap:1rem;flex-wrap:wrap}.metric,.card{background:white;border:1px solid #d8dee9;border-radius:8px;padding:1rem}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:1rem;margin-top:1rem}.ok{color:#147d3f}.warn{color:#a15c00}.err{color:#b42318}code{background:#eef2f7;padding:.1rem .3rem;border-radius:4px}</style>",
            "</head><body>",
            f"<h1>{escape(str(dashboard['title']))}</h1>",
            "<div class=\"metrics\">",
            f"<div class=\"metric\">Reports: {summary['reports']}</div>",
            f"<div class=\"metric err\">Errors: {summary['errors']}</div>",
            f"<div class=\"metric warn\">Warnings: {summary['warnings']}</div>",
            "</div>",
            "<div class=\"grid\">",
            cards or "<p>No JSON or Markdown reports found.</p>",
            "</div></body></html>",
        ]
    )


def render_json(dashboard: dict[str, Any]) -> str:
    return json.dumps(dashboard, indent=2, sort_keys=True)


def _report_card(path: Path) -> dict[str, Any]:
    if path.suffix.lower() == ".json":
        return _json_card(path)
    text = path.read_text(encoding="utf-8", errors="ignore")
    return {
        "path": path.as_posix(),
        "tool": path.stem,
        "kind": "markdown",
        "errors": text.lower().count("error"),
        "warnings": text.lower().count("warning"),
        "summary": text.splitlines()[0] if text.splitlines() else path.name,
    }


def _json_card(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {
            "path": path.as_posix(),
            "tool": path.stem,
            "kind": "json",
            "errors": 1,
            "warnings": 0,
            "summary": f"Unreadable JSON: {exc}",
        }
    summary = data.get("summary", {}) if isinstance(data, dict) else {}
    return {
        "path": path.as_posix(),
        "tool": str(data.get("tool") or data.get("name") or path.stem) if isinstance(data, dict) else path.stem,
        "kind": str(data.get("kind", "json")) if isinstance(data, dict) else "json",
        "errors": int(summary.get("errors", summary.get("error_count", 0))) if isinstance(summary, dict) else 0,
        "warnings": int(summary.get("warnings", summary.get("warning_count", 0))) if isinstance(summary, dict) else 0,
        "summary": _summary_text(summary),
    }


def _summary_text(summary: object) -> str:
    if not isinstance(summary, dict):
        return ""
    parts = [f"{key}: {value}" for key, value in sorted(summary.items()) if isinstance(value, (str, int, float))]
    return ", ".join(parts[:5])


def _card(report: dict[str, Any]) -> str:
    level = "err" if int(report["errors"]) else "warn" if int(report["warnings"]) else "ok"
    return (
        f"<section class=\"card\"><h2>{escape(str(report['tool']))}</h2>"
        f"<p><code>{escape(str(report['path']))}</code></p>"
        f"<p class=\"{level}\">Errors: {report['errors']} | Warnings: {report['warnings']}</p>"
        f"<p>{escape(str(report.get('summary', '')))}</p></section>"
    )
