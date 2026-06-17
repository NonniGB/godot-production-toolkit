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
    scenario_counts = _scenario_summary_counts(reports)
    summary = {
        "reports": len(reports),
        "images": len(images),
        "errors": sum(int(report.get("errors", 0)) for report in reports),
        "warnings": sum(int(report.get("warnings", 0)) for report in reports),
        "reports_with_commands": sum(1 for report in reports if report.get("commands")),
        **status_counts,
        **scenario_counts,
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
            "<style>body{font-family:system-ui,sans-serif;margin:2rem;color:#172033;background:#f7f8fb}.metrics{display:flex;gap:1rem;flex-wrap:wrap}.metric,.card{background:white;border:1px solid #d8dee9;border-radius:8px;padding:1rem}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:1rem;margin-top:1rem}.ok,.ready{color:#147d3f}.warn,.attention{color:#a15c00}.err,.blocked{color:#b42318}.status{font-weight:700;text-transform:uppercase;letter-spacing:.04em}code{background:#eef2f7;padding:.1rem .3rem;border-radius:4px}pre{background:#111827;color:#f9fafb;padding:.75rem;border-radius:6px;white-space:pre-wrap;word-break:break-word}.gallery{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1rem;margin-top:1rem}.image-card img{max-width:100%;border:1px solid #d8dee9;border-radius:6px;background:#111827}.image-card p{word-break:break-word}a{color:#2754c5}table{border-collapse:collapse;width:100%;margin:.5rem 0}td,th{border-top:1px solid #d8dee9;padding:.35rem;text-align:left}dt{font-weight:700}dd{margin:0 0 .35rem}</style>",
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
            f"<div class=\"metric\">Reports with commands: {summary.get('reports_with_commands', 0)}</div>",
            f"<div class=\"metric\">Scenario bundles: {summary['scenario_bundles']}</div>",
            f"<div class=\"metric\">Scenarios: {summary['scenario_passed']}/{summary['scenarios']} passed</div>",
            f"<div class=\"metric\">Telemetry samples: {summary['scenario_telemetry_samples']}</div>",
            f"<div class=\"metric warn\">Telemetry spikes: {summary['scenario_telemetry_spikes']}</div>",
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
    card = {
        "path": path.as_posix(),
        "source_href": _source_href(path, link_base),
        "tool": str(data.get("tool") or data.get("name") or path.stem) if isinstance(data, dict) else path.stem,
        "kind": str(data.get("kind", "json")) if isinstance(data, dict) else "json",
        "errors": errors,
        "warnings": warnings,
        "status": _release_state(errors, warnings),
        "summary": _summary_text(summary),
    }
    if isinstance(data, dict):
        metadata = _report_metadata(data, summary)
        commands = _report_commands(data)
        if metadata:
            card["metadata"] = metadata
        if commands:
            card["commands"] = commands
    if isinstance(data, dict) and data.get("kind") == "scenario_bundle":
        card.update(_scenario_bundle_details(data))
        _apply_scenario_bundle_state(card)
    return card


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


def _report_metadata(data: dict[str, Any], summary: object) -> dict[str, str]:
    summary_dict = summary if isinstance(summary, dict) else {}
    metadata = data.get("metadata", {})
    metadata_dict = metadata if isinstance(metadata, dict) else {}
    rows: dict[str, str] = {}
    for key in ("tool_version", "schema_version", "generated_at", "profile"):
        value = data.get(key, metadata_dict.get(key, summary_dict.get(key)))
        if value not in (None, ""):
            rows[key] = str(value)
    risk = data.get("risk", {})
    risk_dict = risk if isinstance(risk, dict) else {}
    risk_level = summary_dict.get("risk_level", risk_dict.get("level"))
    risk_score = summary_dict.get("risk_score", risk_dict.get("score"))
    if risk_level not in (None, ""):
        rows["risk"] = f"{risk_level} ({risk_score or 0})"
    return rows


def _report_commands(data: dict[str, Any]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    metadata = data.get("metadata", {})
    metadata_dict = metadata if isinstance(metadata, dict) else {}
    for key in ("command", "reproduce_command", "reproduction_command"):
        command = data.get(key, metadata_dict.get(key))
        if isinstance(command, str) and command.strip():
            rows.append({"label": "Reproduce", "command": command.strip()})
    commands = data.get("commands", metadata_dict.get("commands", []))
    if isinstance(commands, list):
        for item in commands:
            if isinstance(item, str) and item.strip():
                rows.append({"label": "Reproduce", "command": item.strip()})
            elif isinstance(item, dict):
                command = str(item.get("command") or "").strip()
                if command:
                    rows.append({"label": str(item.get("label") or "Reproduce"), "command": command})
    return _dedupe_commands(rows)[:5]


def _dedupe_commands(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    seen: set[str] = set()
    unique: list[dict[str, str]] = []
    for row in rows:
        command = row["command"]
        if command in seen:
            continue
        seen.add(command)
        unique.append(row)
    return unique


def _scenario_bundle_details(data: dict[str, Any]) -> dict[str, Any]:
    bundle = data.get("bundle", {})
    if not isinstance(bundle, dict):
        return {}
    evidence = _bundle_evidence_rows(bundle)
    artifacts = _bundle_artifact_rows(bundle)
    summary = data.get("summary", {})
    scenarios = bundle.get("scenarios", [])
    scenario_counts = _scenario_counts(summary, scenarios)
    return {
        "scenario_bundle": {
            **scenario_counts,
            "evidence_links": evidence,
            "artifacts": artifacts,
            "telemetry_summary": _bundle_telemetry_summary(bundle),
            "evidence": len(evidence),
            "evidence_count": len(evidence),
            "artifact_count": len(artifacts),
            "missing_evidence": sum(1 for item in evidence if not item["exists"]),
            "missing_artifacts": sum(1 for item in artifacts if not item["exists"]),
        }
    }


def _scenario_counts(summary: object, scenarios: object) -> dict[str, int]:
    scenario_rows = scenarios if isinstance(scenarios, list) else []
    summary_dict = summary if isinstance(summary, dict) else {}
    return {
        "scenarios": _int_or_default(summary_dict.get("scenarios"), len(scenario_rows)),
        "passed": _int_or_default(summary_dict.get("passed"), _count_status(scenario_rows, "passed")),
        "failed": _int_or_default(summary_dict.get("failed"), _count_status(scenario_rows, "failed")),
        "skipped": _int_or_default(summary_dict.get("skipped"), _count_status(scenario_rows, "skipped")),
    }


def _scenario_summary_counts(reports: list[dict[str, Any]]) -> dict[str, int]:
    bundles = [
        report["scenario_bundle"]
        for report in reports
        if isinstance(report.get("scenario_bundle"), dict)
    ]
    telemetry = [
        bundle["telemetry_summary"]
        for bundle in bundles
        if isinstance(bundle.get("telemetry_summary"), dict)
    ]
    return {
        "scenario_bundles": len(bundles),
        "scenarios": sum(int(bundle.get("scenarios", 0)) for bundle in bundles),
        "scenario_passed": sum(int(bundle.get("passed", 0)) for bundle in bundles),
        "scenario_failed": sum(int(bundle.get("failed", 0)) for bundle in bundles),
        "scenario_evidence": sum(int(bundle.get("evidence", 0)) for bundle in bundles),
        "scenario_telemetry_bundles": len(telemetry),
        "scenario_telemetry_samples": sum(int(item.get("samples", 0)) for item in telemetry),
        "scenario_telemetry_spikes": sum(int(item.get("spikes", 0)) for item in telemetry),
        "scenario_telemetry_warnings": sum(int(item.get("warnings", 0)) for item in telemetry),
        "scenario_telemetry_errors": sum(int(item.get("errors", 0)) for item in telemetry),
    }


def _apply_scenario_bundle_state(card: dict[str, Any]) -> None:
    bundle = card.get("scenario_bundle")
    if not isinstance(bundle, dict):
        return
    if int(bundle.get("failed", 0)) > 0:
        card["status"] = "blocked"
    elif int(bundle.get("missing_evidence", 0)) + int(bundle.get("missing_artifacts", 0)) > 0:
        card["status"] = "attention"


def _int_or_default(value: object, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _count_status(rows: list[object], status: str) -> int:
    return sum(
        1
        for row in rows
        if isinstance(row, dict) and str(row.get("status", "")).lower() == status
    )


def _bundle_evidence_rows(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    links = bundle.get("links", {})
    if isinstance(links, dict):
        for kind, item in sorted(links.items()):
            if isinstance(item, dict):
                rows.append(_evidence_row(kind, item))
    for item in bundle.get("evidence_links", []):
        if isinstance(item, dict):
            rows.append(_evidence_row(str(item.get("kind") or "evidence"), item))
    return rows


def _evidence_row(kind: str, item: dict[str, Any]) -> dict[str, Any]:
    row: dict[str, Any] = {
        "kind": str(item.get("kind") or kind),
        "path": str(item.get("relative_path") or item.get("path") or ""),
        "exists": bool(item.get("exists")),
    }
    if "size_bytes" in item:
        row["size_bytes"] = item["size_bytes"]
    if "is_dir" in item:
        row["is_dir"] = bool(item["is_dir"])
    return row


def _bundle_artifact_rows(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    scenarios = bundle.get("scenarios", [])
    if not isinstance(scenarios, list):
        return rows
    for scenario in scenarios:
        if not isinstance(scenario, dict):
            continue
        scenario_name = str(scenario.get("scenario") or "")
        artifacts = scenario.get("bundle_artifacts", [])
        if not isinstance(artifacts, list):
            continue
        for artifact in artifacts:
            if isinstance(artifact, dict):
                rows.append(
                    {
                        "scenario": scenario_name,
                        "path": str(artifact.get("path") or ""),
                        "exists": bool(artifact.get("exists")),
                    }
                )
    return rows


def _bundle_telemetry_summary(bundle: dict[str, Any]) -> dict[str, Any] | None:
    telemetry = bundle.get("telemetry_summary")
    if not isinstance(telemetry, dict):
        return None
    return {
        "path": str(telemetry.get("relative_path") or telemetry.get("path") or ""),
        "kind": str(telemetry.get("kind") or ""),
        "samples": _int_or_default(telemetry.get("samples"), 0),
        "frame_p95_ms": _float_or_default(telemetry.get("frame_p95_ms"), 0.0),
        "frame_max_ms": _float_or_default(telemetry.get("frame_max_ms"), 0.0),
        "memory_max_mb": _float_or_default(telemetry.get("memory_max_mb"), 0.0),
        "spikes": _int_or_default(telemetry.get("spikes"), 0),
        "warnings": _int_or_default(telemetry.get("warnings"), 0),
        "errors": _int_or_default(telemetry.get("errors"), 0),
    }


def _float_or_default(value: object, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


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
    metadata = _metadata_html(report.get("metadata"))
    commands = _commands_html(report.get("commands"))
    scenario_bundle = _scenario_bundle_html(report.get("scenario_bundle"))
    return (
        f"<section class=\"card\"><h2>{escape(str(report['tool']))}</h2>"
        f"<p class=\"status {escape(str(report['status']))}\">{escape(str(report['status']))}</p>"
        f"<p><a href=\"{escape(source_href)}\"><code>{escape(source_href)}</code></a></p>"
        f"<p class=\"{level}\">Errors: {report['errors']} | Warnings: {report['warnings']}</p>"
        f"<p>{escape(str(report.get('summary', '')))}</p>{metadata}{commands}{scenario_bundle}</section>"
    )


def _metadata_html(metadata: object) -> str:
    if not isinstance(metadata, dict) or not metadata:
        return ""
    rows = []
    for key, value in metadata.items():
        label = key.replace("_", " ").capitalize()
        rows.append(f"<dt>{escape(label)}</dt><dd>{escape(str(value))}</dd>")
    return "<h3>Report Metadata</h3><dl>" + "".join(rows) + "</dl>"


def _commands_html(commands: object) -> str:
    if not isinstance(commands, list) or not commands:
        return ""
    parts = ["<h3>Reproduce</h3>"]
    for item in commands:
        if not isinstance(item, dict):
            continue
        label = str(item.get("label") or "Command")
        command = str(item.get("command") or "")
        if command:
            parts.append(f"<p>{escape(label)}</p><pre><code>{escape(command)}</code></pre>")
    return "".join(parts)


def _scenario_bundle_html(bundle: object) -> str:
    if not isinstance(bundle, dict):
        return ""
    evidence = bundle.get("evidence_links", [])
    artifacts = bundle.get("artifacts", [])
    telemetry = bundle.get("telemetry_summary")
    parts = [
        "<div class=\"bundle-details\">",
        "<h3>Scenario Bundle Evidence</h3>",
        "<p>"
        f"Scenarios: {int(bundle.get('passed', 0))} passed / {int(bundle.get('scenarios', 0))} total | "
        f"Failed: {int(bundle.get('failed', 0))} | "
        f"Evidence: {int(bundle.get('evidence', 0))}"
        "</p>",
        "<p>"
        f"Evidence: {int(bundle.get('evidence_count', 0))} | "
        f"Missing evidence: {int(bundle.get('missing_evidence', 0))} | "
        f"Artifacts: {int(bundle.get('artifact_count', 0))} | "
        f"Missing artifacts: {int(bundle.get('missing_artifacts', 0))}"
        "</p>",
    ]
    if isinstance(telemetry, dict):
        parts.extend(
            [
                "<p>"
                f"Telemetry: {int(telemetry.get('samples', 0))} samples | "
                f"frame p95 {_format_number(telemetry.get('frame_p95_ms'))} ms | "
                f"max {_format_number(telemetry.get('frame_max_ms'))} ms | "
                f"spikes {int(telemetry.get('spikes', 0))}"
                "</p>",
            ]
        )
    if isinstance(evidence, list) and evidence:
        parts.append("<table><thead><tr><th>Kind</th><th>Path</th><th>Exists</th><th>Size</th></tr></thead><tbody>")
        for item in evidence:
            if isinstance(item, dict):
                parts.append(
                    "<tr>"
                    f"<td>{escape(str(item.get('kind', '')))}</td>"
                    f"<td><code>{escape(str(item.get('path', '')))}</code></td>"
                    f"<td>{escape(str(item.get('exists', False)).lower())}</td>"
                    f"<td>{escape(str(item.get('size_bytes', '-')))}</td>"
                    "</tr>"
                )
        parts.append("</tbody></table>")
    if isinstance(artifacts, list) and artifacts:
        parts.append("<table><thead><tr><th>Scenario</th><th>Artifact</th><th>Exists</th></tr></thead><tbody>")
        for item in artifacts:
            if isinstance(item, dict):
                parts.append(
                    "<tr>"
                    f"<td>{escape(str(item.get('scenario', '')))}</td>"
                    f"<td><code>{escape(str(item.get('path', '')))}</code></td>"
                    f"<td>{escape(str(item.get('exists', False)).lower())}</td>"
                    "</tr>"
                )
        parts.append("</tbody></table>")
    parts.append("</div>")
    return "".join(parts)


def _format_number(value: object) -> str:
    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return "0.00"


def _image(image: dict[str, Any]) -> str:
    return (
        f"<section class=\"card image-card\"><h2>{escape(str(image['name']))}</h2>"
        f"<img src=\"{escape(str(image['data_uri']))}\" alt=\"{escape(str(image['name']))}\">"
        f"<p><code>{escape(str(image['path']))}</code></p>"
        f"<p>{int(image['size_bytes'])} bytes</p></section>"
    )
