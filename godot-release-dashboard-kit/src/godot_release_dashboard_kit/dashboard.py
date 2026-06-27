from __future__ import annotations

import base64
from html import escape
import json
import os
from pathlib import Path
import re
from typing import Any

from . import __version__


REPORT_EXTENSIONS = {".json", ".md"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".svg", ".webp"}
WORKFLOW_RULES = (
    ("project", "Project overview", ("godot-project-doctor", "project-doctor")),
    ("export", "Export and packaging", ("export", "preset")),
    ("assets", "Assets and imports", ("asset", "sprite", "pixel")),
    ("input", "Input", ("input",)),
    ("mobile", "Mobile and touch UI", ("mobile", "touch", "safe-area", "localization", "locale")),
    ("content", "Data and content", ("content-graph", "content_graph", "pack", "mod")),
    ("save", "Save compatibility", ("save", "schema", "migration")),
    ("runtime", "Runtime evidence", ("scenario", "telemetry", "visual-smoke", "visual_smoke", "perf")),
    ("refactor", "Refactor safety", ("architecture", "scene", "signal", "gdscript")),
)
DEFAULT_WORKFLOW = {"id": "general", "label": "General reports"}
EXPORT_ARTIFACT_KINDS = {"exported_folder_inspection", "exported_file_list_inspection"}


def build_dashboard(
    reports_dir: Path,
    title: str = "Godot Release Dashboard",
    output_dir: Path | None = None,
    baseline_dir: Path | None = None,
    description: str | None = None,
    project: str | None = None,
) -> dict[str, Any]:
    link_base = output_dir or reports_dir
    reports = [
        _report_card(path, link_base, reports_dir)
        for path in sorted(reports_dir.rglob("*"))
        if path.suffix.lower() in REPORT_EXTENSIONS
    ]
    baseline_reports = (
        [
            _report_card(path, link_base, baseline_dir)
            for path in sorted(baseline_dir.rglob("*"))
            if path.suffix.lower() in REPORT_EXTENSIONS
        ]
        if baseline_dir is not None
        else []
    )
    images = [_image_card(path) for path in sorted(reports_dir.rglob("*")) if path.suffix.lower() in IMAGE_EXTENSIONS]
    status_counts = {
        "blocked": sum(1 for report in reports if report["status"] == "blocked"),
        "attention": sum(1 for report in reports if report["status"] == "attention"),
        "ready": sum(1 for report in reports if report["status"] == "ready"),
    }
    scenario_counts = _scenario_summary_counts(reports)
    export_artifact_counts = _export_artifact_summary_counts(reports)
    workflow_groups = _workflow_groups(reports)
    trends = _trend_summary(reports, baseline_reports)
    summary = {
        "reports": len(reports),
        "images": len(images),
        "errors": sum(int(report.get("errors", 0)) for report in reports),
        "warnings": sum(int(report.get("warnings", 0)) for report in reports),
        "reports_with_commands": sum(1 for report in reports if report.get("commands")),
        "workflows": len(workflow_groups),
        "trend_changes": trends["summary"]["changes"],
        "trend_regressions": trends["summary"]["regressions"],
        "trend_improvements": trends["summary"]["improvements"],
        **status_counts,
        **scenario_counts,
        **export_artifact_counts,
    }
    dashboard = {
        "tool": "godot-release-dashboard-kit",
        "tool_version": __version__,
        "schema_version": "1.0",
        "kind": "release_dashboard",
        "title": title,
        "summary": summary,
        "trends": trends,
        "workflows": workflow_groups,
        "reports": reports,
        "images": images,
    }
    if description:
        dashboard["description"] = description
    if project:
        dashboard["project"] = project
    if baseline_dir is not None:
        dashboard["previous_summary"] = _previous_summary(baseline_reports)
    return dashboard


def render_html(dashboard: dict[str, Any]) -> str:
    report_sections = _workflow_sections(dashboard.get("workflows", []))
    image_cards = "\n".join(_image(image) for image in dashboard.get("images", []))
    trend_section = _trend_section(dashboard.get("trends"))
    filter_controls = _filter_controls(dashboard)
    summary = dashboard["summary"]
    description = str(dashboard.get("description") or "").strip()
    project = str(dashboard.get("project") or "").strip()
    project_html = f"<p><strong>{escape(project)}</strong></p>" if project else ""
    description_html = f"<p>{escape(description)}</p>" if description else ""
    return "\n".join(
        [
            "<!doctype html>",
            "<html lang=\"en\"><head><meta charset=\"utf-8\">",
            f"<title>{escape(str(dashboard['title']))}</title>",
            "<link rel=\"icon\" href=\"data:,\">",
            "<style>body{font-family:system-ui,sans-serif;margin:2rem;color:#172033;background:#f7f8fb}.metrics,.filter-buttons{display:flex;gap:1rem;flex-wrap:wrap}.metric,.card,.filters{background:white;border:1px solid #d8dee9;border-radius:8px;padding:1rem}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:1rem;margin-top:1rem}.workflow{margin-top:1.5rem}.workflow-summary,.muted{color:#4b5563}.ok,.ready,.improvement{color:#147d3f}.warn,.attention{color:#a15c00}.err,.blocked,.regression{color:#b42318}.neutral{color:#2754c5}.status{font-weight:700;text-transform:uppercase;letter-spacing:.04em}.tag{display:inline-block;background:#eef2f7;border-radius:999px;padding:.15rem .45rem;font-size:.85rem}.filters{margin-top:1rem}.filters button{border:1px solid #cbd5e1;background:#f8fafc;border-radius:6px;padding:.35rem .6rem;cursor:pointer}.filters button:hover{background:#eef2f7}.report-hidden{display:none}.trend-bar{display:flex;overflow:hidden;border-radius:6px;background:#e5e7eb;margin:.35rem 0 .75rem}.trend-segment{display:inline-block;min-width:2.5rem;padding:.25rem .4rem;color:white;font-size:.85rem;white-space:nowrap}.trend-segment.ok{background:#147d3f}.trend-segment.warn{background:#a15c00}.trend-segment.err{background:#b42318}code{background:#eef2f7;padding:.1rem .3rem;border-radius:4px}pre{background:#111827;color:#f9fafb;padding:.75rem;border-radius:6px;white-space:pre-wrap;word-break:break-word}.gallery{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1rem;margin-top:1rem}.image-card img{max-width:100%;border:1px solid #d8dee9;border-radius:6px;background:#111827}.image-card p{word-break:break-word}a{color:#2754c5}table{border-collapse:collapse;width:100%;margin:.5rem 0}td,th{border-top:1px solid #d8dee9;padding:.35rem;text-align:left}dt{font-weight:700}dd{margin:0 0 .35rem}</style>",
            "<script>function showAllReports(){document.querySelectorAll('[data-report-card]').forEach(function(card){card.classList.remove('report-hidden')})}function filterReports(kind,value){document.querySelectorAll('[data-report-card]').forEach(function(card){card.classList.toggle('report-hidden',card.dataset[kind]!==value)})}</script>",
            "</head><body>",
            f"<h1>{escape(str(dashboard['title']))}</h1>",
            project_html,
            description_html,
            "<h2>Release Readiness</h2>",
            "<div class=\"metrics\">",
            f"<div class=\"metric blocked\">Blocked: {summary['blocked']}</div>",
            f"<div class=\"metric attention\">Needs attention: {summary['attention']}</div>",
            f"<div class=\"metric ready\">Ready: {summary['ready']}</div>",
            f"<div class=\"metric\">Reports: {summary['reports']}</div>",
            f"<div class=\"metric\">Workflows: {summary.get('workflows', 0)}</div>",
            f"<div class=\"metric\">Images: {summary['images']}</div>",
            f"<div class=\"metric err\">Errors: {summary['errors']}</div>",
            f"<div class=\"metric warn\">Warnings: {summary['warnings']}</div>",
            f"<div class=\"metric\">Reports with commands: {summary.get('reports_with_commands', 0)}</div>",
            f"<div class=\"metric\">Changes: {summary.get('trend_changes', 0)}</div>",
            f"<div class=\"metric err\">Regressions: {summary.get('trend_regressions', 0)}</div>",
            f"<div class=\"metric ok\">Improvements: {summary.get('trend_improvements', 0)}</div>",
            f"<div class=\"metric\">Scenario bundles: {summary['scenario_bundles']}</div>",
            f"<div class=\"metric\">Scenarios: {summary['scenario_passed']}/{summary['scenarios']} passed</div>",
            f"<div class=\"metric warn\">Flaky scenarios: {summary.get('scenario_flaky', 0)}</div>",
            f"<div class=\"metric warn\">Retried scenarios: {summary.get('scenario_retried', 0)}</div>",
            f"<div class=\"metric\">Telemetry samples: {summary['scenario_telemetry_samples']}</div>",
            f"<div class=\"metric warn\">Telemetry spikes: {summary['scenario_telemetry_spikes']}</div>",
            f"<div class=\"metric\">Export artifact reports: {summary.get('export_artifact_reports', 0)}</div>",
            f"<div class=\"metric\">Export files: {summary.get('export_artifact_files', 0)}</div>",
            f"<div class=\"metric\">Files with SHA-256: {summary.get('export_artifact_hashed_files', 0)}</div>",
            f"<div class=\"metric warn\">Private export findings: {summary.get('export_artifact_private_findings', 0)}</div>",
            f"<div class=\"metric warn\">Development file findings: {summary.get('export_artifact_dev_findings', 0)}</div>",
            "</div>",
            filter_controls,
            trend_section,
            "<h2>Reports</h2>",
            report_sections or "<p>No JSON or Markdown reports found.</p>",
            "<h2>Visual Artifacts</h2>",
            "<div class=\"gallery\">",
            image_cards or "<p>No PNG, JPG, SVG, or WebP artifacts found.</p>",
            "</div></body></html>",
        ]
    )


def render_json(dashboard: dict[str, Any]) -> str:
    return json.dumps(dashboard, indent=2, sort_keys=True)


def _report_card(path: Path, link_base: Path, reports_root: Path) -> dict[str, Any]:
    if path.suffix.lower() == ".json":
        return _json_card(path, link_base, reports_root)
    text = path.read_text(encoding="utf-8", errors="ignore")
    return {
        "path": path.as_posix(),
        "report_key": _report_key(path, reports_root),
        "source_href": _source_href(path, link_base),
        "tool": path.stem,
        "kind": "markdown",
        "errors": text.lower().count("error"),
        "warnings": text.lower().count("warning"),
        "status": _release_state(text.lower().count("error"), text.lower().count("warning")),
        "summary": text.splitlines()[0] if text.splitlines() else path.name,
        **_workflow_for(path.stem, "markdown", path.as_posix()),
    }


def _json_card(path: Path, link_base: Path, reports_root: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {
            "path": path.as_posix(),
            "report_key": _report_key(path, reports_root),
            "source_href": _source_href(path, link_base),
            "tool": path.stem,
            "kind": "json",
            "errors": 1,
            "warnings": 0,
            "status": "blocked",
            "summary": f"Unreadable JSON: {exc}",
            **_workflow_for(path.stem, "json", path.as_posix()),
        }
    summary = data.get("summary", {}) if isinstance(data, dict) else {}
    errors = int(summary.get("errors", summary.get("error_count", 0))) if isinstance(summary, dict) else 0
    warnings = int(summary.get("warnings", summary.get("warning_count", 0))) if isinstance(summary, dict) else 0
    workflow, category = _explicit_grouping(data, summary) if isinstance(data, dict) else (None, None)
    card = {
        "path": path.as_posix(),
        "report_key": _report_key(path, reports_root),
        "source_href": _source_href(path, link_base),
        "tool": str(data.get("tool") or data.get("name") or path.stem) if isinstance(data, dict) else path.stem,
        "kind": str(data.get("kind", "json")) if isinstance(data, dict) else "json",
        "errors": errors,
        "warnings": warnings,
        "status": _release_state(errors, warnings),
        "summary": _summary_text(summary),
        **_workflow_for(
            str(data.get("tool") or data.get("name") or path.stem) if isinstance(data, dict) else path.stem,
            str(data.get("kind", "json")) if isinstance(data, dict) else "json",
            path.as_posix(),
            workflow,
            category,
        ),
    }
    if isinstance(data, dict):
        metadata = _report_metadata(data, summary)
        commands = _report_commands(data)
        highlights = _report_highlights(data, summary)
        if metadata:
            card["metadata"] = metadata
        if commands:
            card["commands"] = commands
        if highlights:
            card["highlights"] = highlights
    if isinstance(data, dict) and data.get("kind") == "scenario_bundle":
        card.update(_scenario_bundle_details(data))
        _apply_scenario_bundle_state(card)
    if isinstance(data, dict) and data.get("kind") == "flake_compare":
        card.update(_scenario_flake_details(data))
        _apply_scenario_flake_state(card)
    if isinstance(data, dict) and data.get("kind") in EXPORT_ARTIFACT_KINDS:
        card.update(_export_artifact_details(data))
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


def _workflow_for(
    tool: str,
    kind: str,
    path: str,
    workflow: object = None,
    category: object = None,
) -> dict[str, str]:
    explicit_workflow = str(workflow or "").strip()
    explicit_category = str(category or "").strip()
    if explicit_workflow:
        row = {"workflow_id": _slug(explicit_workflow), "workflow_label": explicit_workflow}
        if explicit_category:
            row["category"] = explicit_category
        return row
    haystack = f"{tool} {kind} {path}".lower()
    for workflow_id, label, needles in WORKFLOW_RULES:
        if any(needle in haystack for needle in needles):
            row = {"workflow_id": workflow_id, "workflow_label": label}
            if explicit_category:
                row["category"] = explicit_category
            return row
    row = {"workflow_id": DEFAULT_WORKFLOW["id"], "workflow_label": DEFAULT_WORKFLOW["label"]}
    if explicit_category:
        row["category"] = explicit_category
    return row


def _explicit_grouping(data: dict[str, Any], summary: object) -> tuple[object, object]:
    metadata = data.get("metadata", {})
    metadata_dict = metadata if isinstance(metadata, dict) else {}
    summary_dict = summary if isinstance(summary, dict) else {}
    return (
        data.get("workflow", metadata_dict.get("workflow", summary_dict.get("workflow"))),
        data.get("category", metadata_dict.get("category", summary_dict.get("category"))),
    )


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or DEFAULT_WORKFLOW["id"]


def _workflow_groups(reports: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    order = [rule[0] for rule in WORKFLOW_RULES] + [DEFAULT_WORKFLOW["id"]]
    for report in reports:
        workflow_id = str(report.get("workflow_id") or DEFAULT_WORKFLOW["id"])
        group = grouped.setdefault(
            workflow_id,
            {
                "id": workflow_id,
                "label": str(report.get("workflow_label") or DEFAULT_WORKFLOW["label"]),
                "reports": [],
                "blocked": 0,
                "attention": 0,
                "ready": 0,
                "errors": 0,
                "warnings": 0,
            },
        )
        group["reports"].append(report)
        status = str(report.get("status") or "ready")
        if status in {"blocked", "attention", "ready"}:
            group[status] += 1
        group["errors"] += int(report.get("errors", 0))
        group["warnings"] += int(report.get("warnings", 0))
    return sorted(
        grouped.values(),
        key=lambda group: (order.index(str(group["id"])) if str(group["id"]) in order else len(order), str(group["label"])),
    )


def _trend_summary(current_reports: list[dict[str, Any]], previous_reports: list[dict[str, Any]]) -> dict[str, Any]:
    if not previous_reports:
        return {
            "enabled": False,
            "summary": {"changes": 0, "regressions": 0, "improvements": 0},
            "changes": [],
        }
    previous_by_key = {str(report.get("report_key") or ""): report for report in previous_reports}
    current_by_key = {str(report.get("report_key") or ""): report for report in current_reports}
    changes: list[dict[str, Any]] = []
    for key in sorted(set(previous_by_key) | set(current_by_key)):
        if not key:
            continue
        previous = previous_by_key.get(key)
        current = current_by_key.get(key)
        change = _report_change(key, previous, current)
        if change is not None:
            changes.append(change)
    return {
        "enabled": True,
        "previous_reports": len(previous_reports),
        "current_reports": len(current_reports),
        "summary": {
            "changes": len(changes),
            "regressions": sum(1 for change in changes if change["direction"] == "regression"),
            "improvements": sum(1 for change in changes if change["direction"] == "improvement"),
        },
        "status_counts": [
            _trend_status_counts("Previous", previous_reports),
            _trend_status_counts("Current", current_reports),
        ],
        "status_deltas": _trend_status_deltas(previous_reports, current_reports),
        "changes": changes[:25],
    }


def _previous_summary(reports: list[dict[str, Any]]) -> dict[str, int]:
    status_counts = {
        "blocked": sum(1 for report in reports if report["status"] == "blocked"),
        "attention": sum(1 for report in reports if report["status"] == "attention"),
        "ready": sum(1 for report in reports if report["status"] == "ready"),
    }
    return {
        "reports": len(reports),
        "errors": sum(int(report.get("errors", 0)) for report in reports),
        "warnings": sum(int(report.get("warnings", 0)) for report in reports),
        **status_counts,
        **_scenario_summary_counts(reports),
        **_export_artifact_summary_counts(reports),
    }


def _trend_status_counts(label: str, reports: list[dict[str, Any]]) -> dict[str, int | str]:
    return {
        "label": label,
        "reports": len(reports),
        "blocked": sum(1 for report in reports if report["status"] == "blocked"),
        "attention": sum(1 for report in reports if report["status"] == "attention"),
        "ready": sum(1 for report in reports if report["status"] == "ready"),
        "errors": sum(int(report.get("errors", 0)) for report in reports),
        "warnings": sum(int(report.get("warnings", 0)) for report in reports),
    }


def _trend_status_deltas(
    previous_reports: list[dict[str, Any]],
    current_reports: list[dict[str, Any]],
) -> dict[str, int]:
    previous = _trend_status_counts("Previous", previous_reports)
    current = _trend_status_counts("Current", current_reports)
    keys = ("reports", "blocked", "attention", "ready", "errors", "warnings")
    return {key: int(current[key]) - int(previous[key]) for key in keys}


def _report_change(
    key: str,
    previous: dict[str, Any] | None,
    current: dict[str, Any] | None,
) -> dict[str, Any] | None:
    if current is None and previous is not None:
        return {
            "report_key": key,
            "tool": str(previous.get("tool") or key),
            "workflow_label": str(previous.get("workflow_label") or DEFAULT_WORKFLOW["label"]),
            "change": "removed",
            "direction": "improvement" if previous.get("status") != "ready" else "neutral",
            "previous_status": previous.get("status"),
            "current_status": None,
            "previous_errors": int(previous.get("errors", 0)),
            "current_errors": 0,
            "error_delta": -int(previous.get("errors", 0)),
            "previous_warnings": int(previous.get("warnings", 0)),
            "current_warnings": 0,
            "warning_delta": -int(previous.get("warnings", 0)),
        }
    if previous is None and current is not None:
        current_status = str(current.get("status") or "ready")
        return {
            "report_key": key,
            "tool": str(current.get("tool") or key),
            "workflow_label": str(current.get("workflow_label") or DEFAULT_WORKFLOW["label"]),
            "change": "added",
            "direction": "regression" if current_status != "ready" else "neutral",
            "previous_status": None,
            "current_status": current_status,
            "previous_errors": 0,
            "current_errors": int(current.get("errors", 0)),
            "error_delta": int(current.get("errors", 0)),
            "previous_warnings": 0,
            "current_warnings": int(current.get("warnings", 0)),
            "warning_delta": int(current.get("warnings", 0)),
        }
    if previous is None or current is None:
        return None
    previous_errors = int(previous.get("errors", 0))
    current_errors = int(current.get("errors", 0))
    previous_warnings = int(previous.get("warnings", 0))
    current_warnings = int(current.get("warnings", 0))
    previous_status = str(previous.get("status") or "ready")
    current_status = str(current.get("status") or "ready")
    error_delta = current_errors - previous_errors
    warning_delta = current_warnings - previous_warnings
    status_delta = _status_rank(current_status) - _status_rank(previous_status)
    if error_delta == 0 and warning_delta == 0 and status_delta == 0:
        return None
    return {
        "report_key": key,
        "tool": str(current.get("tool") or previous.get("tool") or key),
        "workflow_label": str(current.get("workflow_label") or previous.get("workflow_label") or DEFAULT_WORKFLOW["label"]),
        "change": "changed",
        "direction": _trend_direction(status_delta, error_delta, warning_delta),
        "previous_status": previous_status,
        "current_status": current_status,
        "previous_errors": previous_errors,
        "current_errors": current_errors,
        "error_delta": error_delta,
        "previous_warnings": previous_warnings,
        "current_warnings": current_warnings,
        "warning_delta": warning_delta,
    }


def _status_rank(status: str) -> int:
    return {"ready": 0, "attention": 1, "blocked": 2}.get(status, 0)


def _trend_direction(status_delta: int, error_delta: int, warning_delta: int) -> str:
    if status_delta > 0 or error_delta > 0:
        return "regression"
    if status_delta < 0 or error_delta < 0 or warning_delta < 0:
        return "improvement"
    return "neutral"


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


def _report_highlights(data: dict[str, Any], summary: object) -> list[dict[str, str]]:
    summary_dict = summary if isinstance(summary, dict) else {}
    rows: list[dict[str, str]] = []
    tool = str(data.get("tool") or "").lower()
    kind = str(data.get("kind") or "").lower()
    haystack = f"{tool} {kind}"

    if "runtime" in haystack or "telemetry" in haystack:
        rows.extend(_runtime_highlights(summary_dict))
    if "pack" in haystack or "mod" in haystack:
        rows.extend(_pack_highlights(data, summary_dict))
    if "export" in haystack:
        rows.extend(
            _summary_metric_highlights(
                summary_dict,
                ("presets", "platforms", "variants", "files", "total_bytes", "hashed_files"),
            )
        )
    if "asset" in haystack:
        rows.extend(
            _summary_metric_highlights(
                summary_dict,
                ("asset_count", "image_asset_count", "audio_asset_count", "issue_count"),
            )
        )
    if "content" in haystack:
        rows.extend(
            _summary_metric_highlights(
                summary_dict,
                ("collections", "items", "references", "unused", "missing_references"),
            )
        )
    if "save" in haystack:
        rows.extend(_summary_metric_highlights(summary_dict, ("fixtures", "migrations", "validated", "redacted")))
    if "godot-scenario-report-kit" in tool or kind in {"scenario_bundle", "flake_compare"}:
        rows.extend(
            _summary_metric_highlights(
                summary_dict,
                ("scenarios", "passed", "failed", "flaky", "retried", "linked_evidence", "artifacts"),
            )
        )
    if not rows:
        rows.extend(_summary_metric_highlights(summary_dict, ("findings", "reports", "scenarios", "samples")))

    return _dedupe_highlights(rows)[:8]


def _runtime_highlights(summary: dict[str, Any]) -> list[dict[str, str]]:
    rows = _summary_metric_highlights(summary, ("samples", "spikes", "frame_budget_ms", "memory_budget_mb"))
    scenarios = summary.get("scenarios")
    if isinstance(scenarios, list):
        rows.append({"label": "Scenarios", "value": str(len(scenarios))})
    frame_ms = summary.get("frame_ms")
    if isinstance(frame_ms, dict):
        if "p95" in frame_ms:
            rows.append({"label": "Frame p95", "value": f"{_float_or_default(frame_ms.get('p95'), 0.0):.2f} ms"})
        if "max" in frame_ms:
            rows.append({"label": "Frame max", "value": f"{_float_or_default(frame_ms.get('max'), 0.0):.2f} ms"})
    memory_mb = summary.get("memory_mb")
    if isinstance(memory_mb, dict) and "max" in memory_mb:
        rows.append({"label": "Memory max", "value": f"{_float_or_default(memory_mb.get('max'), 0.0):.1f} MB"})
    return rows


def _pack_highlights(data: dict[str, Any], summary: dict[str, Any]) -> list[dict[str, str]]:
    rows = _summary_metric_highlights(summary, ("packs", "files", "dependencies", "content_ids", "risk_score"))
    risk_level = summary.get("risk_level")
    risk = data.get("risk", {})
    risk_dict = risk if isinstance(risk, dict) else {}
    if risk_level in (None, ""):
        risk_level = risk_dict.get("level")
    if risk_level not in (None, ""):
        rows.append({"label": "Risk", "value": str(risk_level)})
    packs = data.get("packs")
    if isinstance(packs, list) and packs:
        pack_order = [
            str(pack.get("id") or "?")
            for pack in packs
            if isinstance(pack, dict)
        ]
        if pack_order:
            rows.append({"label": "Pack order", "value": " -> ".join(pack_order)})
    return rows


def _summary_metric_highlights(summary: dict[str, Any], keys: tuple[str, ...]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for key in keys:
        value = summary.get(key)
        if value in (None, "", []):
            continue
        rows.append({"label": _metric_label(key), "value": _metric_value(value)})
    return rows


def _metric_label(key: str) -> str:
    labels = {
        "p95": "p95",
        "total_bytes": "Total bytes",
        "risk_score": "Risk score",
        "frame_budget_ms": "Frame budget",
        "memory_budget_mb": "Memory budget",
    }
    return labels.get(key, key.replace("_", " ").capitalize())


def _metric_value(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.2f}"
    if isinstance(value, list):
        return str(len(value))
    return str(value)


def _dedupe_highlights(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    seen: set[tuple[str, str]] = set()
    unique: list[dict[str, str]] = []
    for row in rows:
        key = (row["label"], row["value"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(row)
    return unique


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
    flake_reports = [
        report["scenario_flakes"]
        for report in reports
        if isinstance(report.get("scenario_flakes"), dict)
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
        "scenario_flake_reports": len(flake_reports),
        "scenario_flaky": sum(int(item.get("flaky", 0)) for item in flake_reports),
        "scenario_retried": sum(int(item.get("retried", 0)) for item in flake_reports),
    }


def _export_artifact_details(data: dict[str, Any]) -> dict[str, Any]:
    summary = data.get("summary", {})
    summary_dict = summary if isinstance(summary, dict) else {}
    manifest_rows = _export_artifact_manifest_rows(data.get("file_manifest", []))
    extension_counts = _export_extension_counts(data.get("extensions", {}))
    findings = data.get("findings", [])
    finding_rows = findings if isinstance(findings, list) else []
    total_bytes = sum(int(row.get("size_bytes", 0)) for row in manifest_rows)
    hashed_files = sum(1 for row in manifest_rows if row.get("sha256"))
    return {
        "export_artifacts": {
            "kind": str(data.get("kind") or ""),
            "files": _int_or_default(summary_dict.get("files"), len(manifest_rows)),
            "total_bytes": _int_or_default(summary_dict.get("total_bytes"), total_bytes),
            "hashed_files": _int_or_default(summary_dict.get("hashed_files"), hashed_files),
            "private_findings": _finding_count(finding_rows, ("private", "signing", "keystore", "secret")),
            "dev_findings": _finding_count(finding_rows, ("dev_file", "development", "debug", "log")),
            "local_path_findings": _finding_count(finding_rows, ("local_path", "absolute path", "user path")),
            "extensions": extension_counts,
            "file_manifest": manifest_rows[:25],
        }
    }


def _export_artifact_manifest_rows(manifest: object) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not isinstance(manifest, list):
        return rows
    for item in manifest:
        if not isinstance(item, dict):
            continue
        path = str(item.get("path") or item.get("relative_path") or "").strip()
        if not path:
            continue
        rows.append(
            {
                "path": path,
                "extension": str(item.get("extension") or Path(path).suffix).lower(),
                "size_bytes": _int_or_default(item.get("size_bytes"), 0),
                "sha256": str(item.get("sha256") or "").strip(),
            }
        )
    return rows


def _export_extension_counts(extensions: object) -> dict[str, int]:
    if not isinstance(extensions, dict):
        return {}
    rows: dict[str, int] = {}
    for extension, count in extensions.items():
        key = str(extension or "").strip().lower()
        if key:
            rows[key] = _int_or_default(count, 0)
    return dict(sorted(rows.items()))


def _finding_count(findings: list[object], needles: tuple[str, ...]) -> int:
    count = 0
    for finding in findings:
        if not isinstance(finding, dict):
            continue
        text = f"{finding.get('rule_id', '')} {finding.get('message', '')}".lower()
        if any(needle in text for needle in needles):
            count += 1
    return count


def _export_artifact_summary_counts(reports: list[dict[str, Any]]) -> dict[str, int]:
    artifacts = [
        report["export_artifacts"]
        for report in reports
        if isinstance(report.get("export_artifacts"), dict)
    ]
    return {
        "export_artifact_reports": len(artifacts),
        "export_artifact_files": sum(int(item.get("files", 0)) for item in artifacts),
        "export_artifact_hashed_files": sum(int(item.get("hashed_files", 0)) for item in artifacts),
        "export_artifact_private_findings": sum(int(item.get("private_findings", 0)) for item in artifacts),
        "export_artifact_dev_findings": sum(int(item.get("dev_findings", 0)) for item in artifacts),
        "export_artifact_local_path_findings": sum(int(item.get("local_path_findings", 0)) for item in artifacts),
    }


def _apply_scenario_bundle_state(card: dict[str, Any]) -> None:
    bundle = card.get("scenario_bundle")
    if not isinstance(bundle, dict):
        return
    if int(bundle.get("failed", 0)) > 0:
        card["status"] = "blocked"
    elif int(bundle.get("missing_evidence", 0)) + int(bundle.get("missing_artifacts", 0)) > 0:
        card["status"] = "attention"


def _scenario_flake_details(data: dict[str, Any]) -> dict[str, Any]:
    summary = data.get("summary", {})
    summary_dict = summary if isinstance(summary, dict) else {}
    flake_groups = _scenario_flake_rows(data.get("flake_groups", []))
    retry_groups = _scenario_retry_rows(data.get("retry_groups", []))
    return {
        "scenario_flakes": {
            "scenarios": _int_or_default(summary_dict.get("scenarios"), 0),
            "passed": _int_or_default(summary_dict.get("passed"), 0),
            "failed": _int_or_default(summary_dict.get("failed"), 0),
            "flaky": _int_or_default(summary_dict.get("flaky"), len(flake_groups)),
            "retried": _int_or_default(summary_dict.get("retried"), len(retry_groups)),
            "errors": _int_or_default(summary_dict.get("errors"), 0),
            "warnings": _int_or_default(summary_dict.get("warnings"), 0),
            "flake_groups": flake_groups,
            "retry_groups": retry_groups,
        }
    }


def _scenario_flake_rows(groups: object) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not isinstance(groups, list):
        return rows
    for group in groups:
        if not isinstance(group, dict):
            continue
        observations = group.get("observations", [])
        rows.append(
            {
                "scenario": str(group.get("scenario") or group.get("name") or ""),
                "statuses": _string_list(group.get("statuses")),
                "observations": len(observations) if isinstance(observations, list) else 0,
            }
        )
    return rows


def _scenario_retry_rows(groups: object) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not isinstance(groups, list):
        return rows
    for group in groups:
        if not isinstance(group, dict):
            continue
        observations = group.get("observations", [])
        attempts = _int_or_default(group.get("attempts"), len(observations) if isinstance(observations, list) else 0)
        rows.append(
            {
                "scenario": str(group.get("scenario") or group.get("name") or ""),
                "run": str(group.get("run") or ""),
                "attempts": attempts,
                "statuses": _string_list(group.get("statuses")),
                "final_status": str(group.get("final_status") or ""),
            }
        )
    return rows


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if item not in (None, "")]


def _apply_scenario_flake_state(card: dict[str, Any]) -> None:
    details = card.get("scenario_flakes")
    if not isinstance(details, dict):
        return
    if int(details.get("errors", 0)) > 0:
        card["status"] = "blocked"
    elif int(details.get("flaky", 0)) + int(details.get("retried", 0)) > 0 and card.get("status") == "ready":
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


def _report_key(path: Path, reports_root: Path) -> str:
    try:
        return path.resolve().relative_to(reports_root.resolve()).as_posix()
    except ValueError:
        return path.name


def _source_href(path: Path, link_base: Path) -> str:
    relative = os.path.relpath(path.resolve(), link_base.resolve())
    return Path(relative).as_posix()


def _trend_section(trends: object) -> str:
    if not isinstance(trends, dict) or not trends.get("enabled"):
        return ""
    changes = trends.get("changes", [])
    summary = trends.get("summary", {})
    if not isinstance(changes, list) or not isinstance(summary, dict):
        return ""
    parts = [
        "<h2>Changes Since Previous Reports</h2>",
        "<div class=\"metrics\">",
        f"<div class=\"metric\">Changed reports: {int(summary.get('changes', 0))}</div>",
        f"<div class=\"metric err\">Regressions: {int(summary.get('regressions', 0))}</div>",
        f"<div class=\"metric ok\">Improvements: {int(summary.get('improvements', 0))}</div>",
        "</div>",
    ]
    status_bars = _trend_status_bars(trends)
    if status_bars:
        parts.append(status_bars)
    if not changes:
        parts.append("<p class=\"muted\">No report status, error, or warning changes found.</p>")
        return "".join(parts)
    parts.append("<div class=\"grid\">")
    for change in changes:
        if isinstance(change, dict):
            parts.append(_trend_card(change))
    parts.append("</div>")
    return "".join(parts)


def _trend_status_bars(trends: dict[str, Any]) -> str:
    rows = trends.get("status_counts")
    deltas = trends.get("status_deltas")
    if not isinstance(rows, list) or not isinstance(deltas, dict):
        return ""
    valid_rows = [row for row in rows if isinstance(row, dict)]
    if len(valid_rows) < 2:
        return ""
    status_keys = (
        ("blocked", "Blocked", "err"),
        ("attention", "Attention", "warn"),
        ("ready", "Ready", "ok"),
    )
    parts = ["<section class=\"card\"><h3>Readiness Trend</h3>"]
    for row in valid_rows:
        total = sum(max(0, int(row.get(key, 0))) for key, _label, _css in status_keys) or 1
        parts.append(
            f"<p><strong>{escape(str(row.get('label') or 'Reports'))}</strong>: "
            f"{int(row.get('reports', 0))} report(s), "
            f"{int(row.get('errors', 0))} error(s), "
            f"{int(row.get('warnings', 0))} warning(s)</p>"
        )
        parts.append("<div class=\"trend-bar\">")
        for key, label, css_class in status_keys:
            count = max(0, int(row.get(key, 0)))
            if count == 0:
                continue
            width = round((count / total) * 100, 2)
            parts.append(
                f"<span class=\"trend-segment {css_class}\" "
                f"data-trend-status=\"{escape(key)}\" style=\"width:{width}%\">"
                f"{escape(label)} {count}</span>"
            )
        parts.append("</div>")
    parts.append(
        "<p class=\"muted\">Delta: "
        f"blocked {_signed_int(deltas.get('blocked', 0))}, "
        f"attention {_signed_int(deltas.get('attention', 0))}, "
        f"ready {_signed_int(deltas.get('ready', 0))}, "
        f"errors {_signed_int(deltas.get('errors', 0))}, "
        f"warnings {_signed_int(deltas.get('warnings', 0))}</p></section>"
    )
    return "".join(parts)


def _trend_card(change: dict[str, Any]) -> str:
    direction = str(change.get("direction") or "neutral")
    tool = str(change.get("tool") or change.get("report_key") or "Report")
    workflow = str(change.get("workflow_label") or DEFAULT_WORKFLOW["label"])
    previous_status = change.get("previous_status") or "none"
    current_status = change.get("current_status") or "none"
    return (
        f"<section class=\"card\"><h3>{escape(tool)}</h3>"
        f"<p class=\"status {escape(direction)}\">{escape(direction)}</p>"
        f"<p><span class=\"tag\">{escape(workflow)}</span> "
        f"<span class=\"tag\">{escape(str(change.get('change', 'changed')))}</span></p>"
        f"<p>Status: {escape(str(previous_status))} -> {escape(str(current_status))}</p>"
        "<p>"
        f"Errors: {int(change.get('previous_errors', 0))} -> {int(change.get('current_errors', 0))} "
        f"({_signed_int(change.get('error_delta', 0))})"
        "</p>"
        "<p>"
        f"Warnings: {int(change.get('previous_warnings', 0))} -> {int(change.get('current_warnings', 0))} "
        f"({_signed_int(change.get('warning_delta', 0))})"
        "</p>"
        f"<p><code>{escape(str(change.get('report_key') or ''))}</code></p></section>"
    )


def _signed_int(value: object) -> str:
    number = _int_or_default(value, 0)
    return f"{number:+d}"


def _workflow_sections(workflows: object) -> str:
    if not isinstance(workflows, list) or not workflows:
        return ""
    sections: list[str] = []
    for workflow in workflows:
        if not isinstance(workflow, dict):
            continue
        reports = workflow.get("reports", [])
        if not isinstance(reports, list) or not reports:
            continue
        cards = "\n".join(_card(report) for report in reports if isinstance(report, dict))
        sections.append(
            "<section class=\"workflow\">"
            f"<h3>{escape(str(workflow.get('label') or 'Reports'))}</h3>"
            "<p class=\"workflow-summary\">"
            f"{len(reports)} report(s), "
            f"{int(workflow.get('blocked', 0))} blocked, "
            f"{int(workflow.get('attention', 0))} attention, "
            f"{int(workflow.get('ready', 0))} ready"
            "</p>"
            f"<div class=\"grid\">{cards}</div>"
            "</section>"
        )
    return "\n".join(sections)


def _filter_controls(dashboard: dict[str, Any]) -> str:
    workflows = dashboard.get("workflows", [])
    workflow_buttons: list[str] = []
    if isinstance(workflows, list):
        for workflow in workflows:
            if not isinstance(workflow, dict):
                continue
            workflow_id = str(workflow.get("id") or "").strip()
            label = str(workflow.get("label") or workflow_id).strip()
            if workflow_id and label:
                workflow_buttons.append(
                    "<button type=\"button\" "
                    f"data-filter-workflow=\"{escape(workflow_id)}\" "
                    f"onclick=\"filterReports('workflow','{escape(workflow_id)}')\">"
                    f"{escape(label)}</button>"
                )
    status_buttons = "".join(
        "<button type=\"button\" "
        f"data-filter-status=\"{status}\" "
        f"onclick=\"filterReports('status','{status}')\">{label}</button>"
        for status, label in (("blocked", "Blocked"), ("attention", "Needs attention"), ("ready", "Ready"))
    )
    workflow_html = "".join(workflow_buttons)
    return (
        "<section class=\"filters\" aria-label=\"Report filters\">"
        "<h2>Filter Reports</h2>"
        "<div class=\"filter-buttons\">"
        "<button type=\"button\" onclick=\"showAllReports()\">All reports</button>"
        f"{status_buttons}{workflow_html}"
        "</div></section>"
    )


def _card(report: dict[str, Any]) -> str:
    level = "err" if int(report["errors"]) else "warn" if int(report["warnings"]) else "ok"
    source_href = str(report["source_href"])
    metadata = _metadata_html(report.get("metadata"))
    highlights = _highlights_html(report.get("highlights"))
    commands = _commands_html(report.get("commands"))
    scenario_bundle = _scenario_bundle_html(report.get("scenario_bundle"))
    scenario_flakes = _scenario_flake_html(report.get("scenario_flakes"))
    export_artifacts = _export_artifact_html(report.get("export_artifacts"))
    workflow = str(report.get("workflow_label") or DEFAULT_WORKFLOW["label"])
    workflow_id = str(report.get("workflow_id") or DEFAULT_WORKFLOW["id"])
    status = str(report["status"])
    category = str(report.get("category") or "").strip()
    category_html = f" <span class=\"tag\">{escape(category)}</span>" if category else ""
    return (
        "<section class=\"card\" data-report-card "
        f"data-status=\"{escape(status)}\" data-workflow=\"{escape(workflow_id)}\">"
        f"<h2>{escape(str(report['tool']))}</h2>"
        f"<p class=\"status {escape(status)}\">{escape(status)}</p>"
        f"<p><span class=\"tag\">{escape(workflow)}</span>{category_html}</p>"
        f"<p><a href=\"{escape(source_href)}\"><code>{escape(source_href)}</code></a></p>"
        f"<p class=\"{level}\">Errors: {report['errors']} | Warnings: {report['warnings']}</p>"
        f"<p>{escape(str(report.get('summary', '')))}</p>"
        f"{highlights}{metadata}{commands}{scenario_bundle}{scenario_flakes}{export_artifacts}</section>"
    )


def _metadata_html(metadata: object) -> str:
    if not isinstance(metadata, dict) or not metadata:
        return ""
    rows = []
    for key, value in metadata.items():
        label = key.replace("_", " ").capitalize()
        rows.append(f"<dt>{escape(label)}</dt><dd>{escape(str(value))}</dd>")
    return "<h3>Report Metadata</h3><dl>" + "".join(rows) + "</dl>"


def _highlights_html(highlights: object) -> str:
    if not isinstance(highlights, list) or not highlights:
        return ""
    rows = []
    for item in highlights:
        if not isinstance(item, dict):
            continue
        label = str(item.get("label") or "").strip()
        value = str(item.get("value") or "").strip()
        if label and value:
            rows.append(f"<dt>{escape(label)}</dt><dd>{escape(value)}</dd>")
    if not rows:
        return ""
    return "<h3>Highlights</h3><dl>" + "".join(rows) + "</dl>"


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


def _scenario_flake_html(details: object) -> str:
    if not isinstance(details, dict):
        return ""
    flake_groups = details.get("flake_groups", [])
    retry_groups = details.get("retry_groups", [])
    parts = [
        "<div class=\"bundle-details\">",
        "<h3>Scenario Flake and Retry Evidence</h3>",
        "<p>"
        f"Scenarios: {int(details.get('passed', 0))} passed / {int(details.get('scenarios', 0))} total | "
        f"Failed: {int(details.get('failed', 0))} | "
        f"Flaky scenarios: {int(details.get('flaky', 0))} | "
        f"Retried scenarios: {int(details.get('retried', 0))}"
        "</p>",
    ]
    if isinstance(flake_groups, list) and flake_groups:
        parts.append("<table><thead><tr><th>Scenario</th><th>Statuses</th><th>Observations</th></tr></thead><tbody>")
        for item in flake_groups:
            if isinstance(item, dict):
                statuses = item.get("statuses", [])
                status_text = ", ".join(str(status) for status in statuses) if isinstance(statuses, list) else ""
                parts.append(
                    "<tr>"
                    f"<td>{escape(str(item.get('scenario', '')))}</td>"
                    f"<td>{escape(status_text)}</td>"
                    f"<td>{int(item.get('observations', 0))}</td>"
                    "</tr>"
                )
        parts.append("</tbody></table>")
    if isinstance(retry_groups, list) and retry_groups:
        parts.append(
            "<table><thead><tr><th>Scenario</th><th>Run</th><th>Attempts</th>"
            "<th>Statuses</th><th>Final status</th></tr></thead><tbody>"
        )
        for item in retry_groups:
            if isinstance(item, dict):
                statuses = item.get("statuses", [])
                status_text = ", ".join(str(status) for status in statuses) if isinstance(statuses, list) else ""
                parts.append(
                    "<tr>"
                    f"<td>{escape(str(item.get('scenario', '')))}</td>"
                    f"<td><code>{escape(str(item.get('run', '')))}</code></td>"
                    f"<td>{int(item.get('attempts', 0))}</td>"
                    f"<td>{escape(status_text)}</td>"
                    f"<td>{escape(str(item.get('final_status', '')))}</td>"
                    "</tr>"
                )
        parts.append("</tbody></table>")
    parts.append("</div>")
    return "".join(parts)


def _export_artifact_html(details: object) -> str:
    if not isinstance(details, dict):
        return ""
    extensions = details.get("extensions", {})
    manifest = details.get("file_manifest", [])
    parts = [
        "<div class=\"bundle-details\">",
        "<h3>Export Artifact Evidence</h3>",
        "<p>"
        f"Files inspected: {int(details.get('files', 0))} | "
        f"Total bytes: {int(details.get('total_bytes', 0))} | "
        f"Files with SHA-256: {int(details.get('hashed_files', 0))}"
        "</p>",
        "<p>"
        f"Private/signing findings: {int(details.get('private_findings', 0))} | "
        f"Development file findings: {int(details.get('dev_findings', 0))} | "
        f"Local path findings: {int(details.get('local_path_findings', 0))}"
        "</p>",
    ]
    if isinstance(extensions, dict) and extensions:
        parts.append("<table><thead><tr><th>Extension</th><th>Files</th></tr></thead><tbody>")
        for extension, count in extensions.items():
            parts.append(
                "<tr>"
                f"<td><code>{escape(str(extension))}</code></td>"
                f"<td>{int(count)}</td>"
                "</tr>"
            )
        parts.append("</tbody></table>")
    if isinstance(manifest, list) and manifest:
        parts.append("<table><thead><tr><th>Path</th><th>Extension</th><th>Size</th><th>SHA-256</th></tr></thead><tbody>")
        for item in manifest:
            if not isinstance(item, dict):
                continue
            sha = str(item.get("sha256") or "")
            sha_label = sha[:12] if sha else "not recorded"
            parts.append(
                "<tr>"
                f"<td><code>{escape(str(item.get('path', '')))}</code></td>"
                f"<td><code>{escape(str(item.get('extension', '')))}</code></td>"
                f"<td>{int(item.get('size_bytes', 0))}</td>"
                f"<td><code>{escape(sha_label)}</code></td>"
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
