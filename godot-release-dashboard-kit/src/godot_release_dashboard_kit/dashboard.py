from __future__ import annotations

import base64
from html import escape
import json
import os
from pathlib import Path
from typing import Any

from . import __version__


REPORT_EXTENSIONS = {".json", ".md"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".svg", ".webp"}


def build_dashboard(
    reports_dir: Path,
    title: str = "Godot Release Dashboard",
    output_dir: Path | None = None,
) -> dict[str, Any]:
    link_base = output_dir or reports_dir
    reports = [
        _report_card(path, link_base)
        for path in sorted(reports_dir.rglob("*"))
        if path.suffix.lower() in REPORT_EXTENSIONS
    ]
    images = [_image_card(path) for path in sorted(reports_dir.rglob("*")) if path.suffix.lower() in IMAGE_EXTENSIONS]
    status_counts = {
        "blocked": sum(1 for report in reports if report["status"] == "blocked"),
        "attention": sum(1 for report in reports if report["status"] == "attention"),
        "ready": sum(1 for report in reports if report["status"] == "ready"),
    }
    summary = {
        "reports": len(reports),
        "images": len(images),
        "errors": sum(int(report.get("errors", 0)) for report in reports),
        "warnings": sum(int(report.get("warnings", 0)) for report in reports),
        **status_counts,
    }
    return {
        "tool": "godot-release-dashboard-kit",
        "tool_version": __version__,
        "schema_version": "1.0",
        "kind": "release_dashboard",
        "title": title,
        "summary": summary,
        "reports": reports,
        "images": images,
    }


def render_html(dashboard: dict[str, Any]) -> str:
    cards = "\n".join(_card(report) for report in dashboard["reports"])
    image_cards = "\n".join(_image(image) for image in dashboard.get("images", []))
    summary = dashboard["summary"]
    return "\n".join(
        [
            "<!doctype html>",
            "<html lang=\"en\"><head><meta charset=\"utf-8\">",
            f"<title>{escape(str(dashboard['title']))}</title>",
            "<link rel=\"icon\" href=\"data:,\">",
            "<style>body{font-family:system-ui,sans-serif;margin:2rem;color:#172033;background:#f7f8fb}.metrics{display:flex;gap:1rem;flex-wrap:wrap}.metric,.card{background:white;border:1px solid #d8dee9;border-radius:8px;padding:1rem}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:1rem;margin-top:1rem}.ok,.ready{color:#147d3f}.warn,.attention{color:#a15c00}.err,.blocked{color:#b42318}.status{font-weight:700;text-transform:uppercase;letter-spacing:.04em}code{background:#eef2f7;padding:.1rem .3rem;border-radius:4px}.gallery{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1rem;margin-top:1rem}.image-card img{max-width:100%;border:1px solid #d8dee9;border-radius:6px;background:#111827}.image-card p{word-break:break-word}a{color:#2754c5}</style>",
            "</head><body>",
            f"<h1>{escape(str(dashboard['title']))}</h1>",
            "<h2>Release Readiness</h2>",
            "<div class=\"metrics\">",
            f"<div class=\"metric blocked\">Blocked: {summary['blocked']}</div>",
            f"<div class=\"metric attention\">Needs attention: {summary['attention']}</div>",
            f"<div class=\"metric ready\">Ready: {summary['ready']}</div>",
            f"<div class=\"metric\">Reports: {summary['reports']}</div>",
            f"<div class=\"metric\">Images: {summary['images']}</div>",
            f"<div class=\"metric err\">Errors: {summary['errors']}</div>",
            f"<div class=\"metric warn\">Warnings: {summary['warnings']}</div>",
            "</div>",
            "<h2>Reports</h2>",
            "<div class=\"grid\">",
            cards or "<p>No JSON or Markdown reports found.</p>",
            "</div>",
            "<h2>Visual Artifacts</h2>",
            "<div class=\"gallery\">",
            image_cards or "<p>No PNG, JPG, SVG, or WebP artifacts found.</p>",
            "</div></body></html>",
        ]
    )


def render_json(dashboard: dict[str, Any]) -> str:
    return json.dumps(dashboard, indent=2, sort_keys=True)


def _report_card(path: Path, link_base: Path) -> dict[str, Any]:
    if path.suffix.lower() == ".json":
        return _json_card(path, link_base)
    text = path.read_text(encoding="utf-8", errors="ignore")
    return {
        "path": path.as_posix(),
        "source_href": _source_href(path, link_base),
        "tool": path.stem,
        "kind": "markdown",
        "errors": text.lower().count("error"),
        "warnings": text.lower().count("warning"),
        "status": _release_state(text.lower().count("error"), text.lower().count("warning")),
        "summary": text.splitlines()[0] if text.splitlines() else path.name,
    }


def _json_card(path: Path, link_base: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {
            "path": path.as_posix(),
            "source_href": _source_href(path, link_base),
            "tool": path.stem,
            "kind": "json",
            "errors": 1,
            "warnings": 0,
            "status": "blocked",
            "summary": f"Unreadable JSON: {exc}",
        }
    summary = data.get("summary", {}) if isinstance(data, dict) else {}
    errors = int(summary.get("errors", summary.get("error_count", 0))) if isinstance(summary, dict) else 0
    warnings = int(summary.get("warnings", summary.get("warning_count", 0))) if isinstance(summary, dict) else 0
    return {
        "path": path.as_posix(),
        "source_href": _source_href(path, link_base),
        "tool": str(data.get("tool") or data.get("name") or path.stem) if isinstance(data, dict) else path.stem,
        "kind": str(data.get("kind", "json")) if isinstance(data, dict) else "json",
        "errors": errors,
        "warnings": warnings,
        "status": _release_state(errors, warnings),
        "summary": _summary_text(summary),
    }


def _image_card(path: Path) -> dict[str, Any]:
    return {
        "path": path.as_posix(),
        "name": path.stem,
        "mime": _mime_type(path),
        "size_bytes": path.stat().st_size,
        "data_uri": _data_uri(path),
    }


def _mime_type(path: Path) -> str:
    extension = path.suffix.lower()
    return {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".svg": "image/svg+xml",
        ".webp": "image/webp",
    }.get(extension, "application/octet-stream")


def _data_uri(path: Path) -> str:
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{_mime_type(path)};base64,{encoded}"


def _summary_text(summary: object) -> str:
    if not isinstance(summary, dict):
        return ""
    parts = [f"{key}: {value}" for key, value in sorted(summary.items()) if isinstance(value, (str, int, float))]
    return ", ".join(parts[:5])


def _release_state(errors: int, warnings: int) -> str:
    if errors:
        return "blocked"
    if warnings:
        return "attention"
    return "ready"


def _source_href(path: Path, link_base: Path) -> str:
    relative = os.path.relpath(path.resolve(), link_base.resolve())
    return Path(relative).as_posix()


def _card(report: dict[str, Any]) -> str:
    level = "err" if int(report["errors"]) else "warn" if int(report["warnings"]) else "ok"
    source_href = str(report["source_href"])
    return (
        f"<section class=\"card\"><h2>{escape(str(report['tool']))}</h2>"
        f"<p class=\"status {escape(str(report['status']))}\">{escape(str(report['status']))}</p>"
        f"<p><a href=\"{escape(source_href)}\"><code>{escape(source_href)}</code></a></p>"
        f"<p class=\"{level}\">Errors: {report['errors']} | Warnings: {report['warnings']}</p>"
        f"<p>{escape(str(report.get('summary', '')))}</p></section>"
    )


def _image(image: dict[str, Any]) -> str:
    return (
        f"<section class=\"card image-card\"><h2>{escape(str(image['name']))}</h2>"
        f"<img src=\"{escape(str(image['data_uri']))}\" alt=\"{escape(str(image['name']))}\">"
        f"<p><code>{escape(str(image['path']))}</code></p>"
        f"<p>{int(image['size_bytes'])} bytes</p></section>"
    )
