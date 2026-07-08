from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .audit import build_readiness_matrix
from . import __version__
from .models import Screen, Thresholds, Viewport
from .rules import rule_catalog


REPORT_SLOTS: dict[str, str] = {
    "input": "Input coverage",
    "export": "Export readiness",
    "localization": "Localization risk",
    "mobile_perf": "Mobile performance",
    "visual_smoke": "Visual smoke",
}


def build_combined_readiness(
    viewports: dict[str, Viewport],
    screens: list[Screen],
    thresholds: Thresholds,
    report_paths: dict[str, Path],
) -> dict[str, Any]:
    matrix = build_readiness_matrix(viewports, screens, thresholds)
    linked_reports = [_linked_report(slot, path) for slot, path in sorted(report_paths.items())]
    summary = {
        "status": _overall_status(matrix["matrix"], linked_reports),
        "screens": matrix["summary"]["screens"],
        "screen_passes": matrix["summary"]["ready"],
        "screen_actions": matrix["summary"]["action"],
        "screen_reviews": matrix["summary"]["review"],
        "linked_reports": len(linked_reports),
        "linked_report_passes": sum(1 for report in linked_reports if report["readiness_status"] == "pass"),
        "linked_report_reviews": sum(1 for report in linked_reports if report["readiness_status"] == "review"),
        "linked_report_actions": sum(1 for report in linked_reports if report["readiness_status"] == "action"),
        "linked_report_errors": sum(int(report["errors"]) for report in linked_reports),
        "linked_report_warnings": sum(int(report["warnings"]) for report in linked_reports),
        "linked_report_findings": sum(int(report["findings"]) for report in linked_reports),
        "missing_reports": sum(1 for report in linked_reports if report["status"] == "missing"),
        "unreadable_reports": sum(1 for report in linked_reports if report["status"] == "unreadable"),
        "errors": matrix["summary"]["errors"] + sum(int(report["errors"]) for report in linked_reports),
        "warnings": matrix["summary"]["warnings"] + sum(int(report["warnings"]) for report in linked_reports),
    }
    return {
        "tool": "godot-mobile-ui-doctor",
        "version": __version__,
        "tool_version": __version__,
        "schema_version": "1.1",
        "metadata": {
            "rules": rule_catalog(),
        },
        "kind": "combined_mobile_readiness",
        "summary": summary,
        "matrix": matrix["matrix"],
        "linked_reports": linked_reports,
        "findings": matrix["findings"],
    }


def render_combined_readiness(report: dict[str, Any], fmt: str) -> str:
    if fmt == "json":
        return json.dumps(report, indent=2, sort_keys=True)
    if fmt == "markdown":
        return _markdown(report)
    return _text(report)


def _linked_report(slot: str, path: Path) -> dict[str, Any]:
    label = REPORT_SLOTS.get(slot, slot.replace("_", " ").title())
    result: dict[str, Any] = {
        "slot": slot,
        "label": label,
        "path": str(path),
        "tool": label,
        "errors": 0,
        "warnings": 0,
        "findings": 0,
        "status": "missing",
        "readiness_status": "action",
    }
    if not path.exists():
        return result
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        result["status"] = "unreadable"
        result["readiness_status"] = "action"
        result["message"] = str(exc)
        result["errors"] = 1
        return result

    errors, warnings = _severity_counts(data)
    result.update(
        {
            "tool": str(data.get("tool") or data.get("name") or label),
            "errors": errors,
            "warnings": warnings,
            "findings": _finding_count(data),
            "rule_summaries": _rule_summaries(data),
            "top_findings": _top_findings(data),
            "status": _status(errors, warnings),
            "readiness_status": _status(errors, warnings),
        }
    )
    return result


def _severity_counts(data: dict[str, Any]) -> tuple[int, int]:
    summary = data.get("summary", {})
    if isinstance(summary, dict):
        errors = int(summary.get("errors", summary.get("error_count", 0)))
        warnings = int(summary.get("warnings", summary.get("warning_count", 0)))
        if errors or warnings:
            return errors, warnings

    errors = 0
    warnings = 0
    for finding in _findings(data):
        severity = str(finding.get("severity", "")).lower()
        if severity == "error":
            errors += 1
        elif severity == "warning":
            warnings += 1
    return errors, warnings


def _finding_count(data: dict[str, Any]) -> int:
    return len(_findings(data))


def _findings(data: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("findings", "issues"):
        value = data.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    return []


def _top_findings(data: dict[str, Any], limit: int = 3) -> list[dict[str, str]]:
    ranked = sorted(_findings(data), key=_finding_rank)
    return [_compact_finding(finding) for finding in ranked[:limit]]


def _rule_summaries(data: dict[str, Any], limit: int = 5) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for finding in _findings(data):
        rule = str(finding.get("rule_id") or finding.get("code") or finding.get("id") or "finding")
        entry = grouped.setdefault(
            rule,
            {
                "rule": rule,
                "severity": "info",
                "findings": 0,
                "sample_message": "",
                "locations": [],
            },
        )
        entry["findings"] += 1
        entry["severity"] = _higher_severity(str(entry["severity"]), str(finding.get("severity", "info")))
        if not entry["sample_message"] and finding.get("message"):
            entry["sample_message"] = str(finding["message"])
        location = _finding_location(finding)
        if location and location not in entry["locations"] and len(entry["locations"]) < 3:
            entry["locations"].append(location)
    return sorted(grouped.values(), key=_rule_summary_rank)[:limit]


def _higher_severity(current: str, candidate: str) -> str:
    rank = {"error": 0, "warning": 1, "info": 2}
    current_key = current.lower()
    candidate_key = candidate.lower()
    return candidate_key if rank.get(candidate_key, 2) < rank.get(current_key, 2) else current_key


def _rule_summary_rank(summary: dict[str, Any]) -> tuple[int, int, str]:
    severity = str(summary["severity"]).lower()
    rank = {"error": 0, "warning": 1}.get(severity, 2)
    return rank, -int(summary["findings"]), str(summary["rule"])


def _finding_rank(finding: dict[str, Any]) -> tuple[int, str]:
    severity = str(finding.get("severity", "")).lower()
    rank = {"error": 0, "warning": 1}.get(severity, 2)
    return rank, str(finding.get("rule_id") or finding.get("code") or finding.get("id") or "")


def _compact_finding(finding: dict[str, Any]) -> dict[str, str]:
    return {
        "severity": str(finding.get("severity", "info")),
        "rule": str(finding.get("rule_id") or finding.get("code") or finding.get("id") or "finding"),
        "message": str(finding.get("message", "")),
        "location": _finding_location(finding),
    }


def _finding_location(finding: dict[str, Any]) -> str:
    parts = []
    for key in ("path", "file", "screen", "viewport", "node", "preset", "preset_name", "action"):
        value = finding.get(key)
        if value:
            parts.append(str(value))
    return " / ".join(parts)


def _status(errors: int, warnings: int) -> str:
    if errors > 0:
        return "action"
    if warnings > 0:
        return "review"
    return "pass"


def _overall_status(matrix_rows: list[dict[str, Any]], linked_reports: list[dict[str, Any]]) -> str:
    statuses = [str(row.get("status", "pass")) for row in matrix_rows]
    statuses.extend(str(report.get("readiness_status", "pass")) for report in linked_reports)
    if "action" in statuses:
        return "action"
    if "review" in statuses:
        return "review"
    return "pass"


def _text(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "Godot Mobile Readiness",
        (
            f"Status: {summary['status']} | Screens: {summary['screens']} | Action: {summary['screen_actions']} | "
            f"Review: {summary['screen_reviews']}"
        ),
        (
            f"Linked reports: {summary['linked_reports']} | "
            f"Action: {summary['linked_report_actions']} | Review: {summary['linked_report_reviews']} | "
            f"Errors: {summary['errors']} | Warnings: {summary['warnings']} | "
            f"Findings: {summary['linked_report_findings']}"
        ),
        "",
        "Screens:",
    ]
    for row in report["matrix"]:
        lines.append(
            f"- {row['screen']} / {row['viewport']}: {row['status']} "
            f"(safe area {row['safe_area']}, touch {row['touch_targets']}, "
            f"text {row['text_fit']}, expansion {row['text_expansion']})"
        )
    if report["linked_reports"]:
        lines.extend(["", "Linked reports:"])
        for item in report["linked_reports"]:
            lines.append(
                f"- {item['label']}: {item['readiness_status']} "
                f"(source status {item['status']}; "
                f"{item['errors']} errors, {item['warnings']} warnings) - {item['path']}"
            )
            for finding in item.get("top_findings", []):
                location = f" [{finding['location']}]" if finding.get("location") else ""
                lines.append(
                    f"  - {finding['severity']} {finding['rule']}{location}: {finding['message']}"
                )
            for rule in item.get("rule_summaries", []):
                locations = ", ".join(rule.get("locations", []))
                suffix = f" ({locations})" if locations else ""
                lines.append(
                    f"  - rule {rule['rule']}: {rule['findings']} finding(s), "
                    f"highest severity {rule['severity']}{suffix}"
                )
    return "\n".join(lines)


def _markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Godot Mobile Readiness",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Overall status | {summary['status']} |",
        f"| Screens | {summary['screens']} |",
        f"| Screens passing | {summary['screen_passes']} |",
        f"| Screens needing action | {summary['screen_actions']} |",
        f"| Screens needing review | {summary['screen_reviews']} |",
        f"| Linked reports | {summary['linked_reports']} |",
        f"| Linked reports passing | {summary['linked_report_passes']} |",
        f"| Linked reports needing action | {summary['linked_report_actions']} |",
        f"| Linked reports needing review | {summary['linked_report_reviews']} |",
        f"| Linked report findings | {summary['linked_report_findings']} |",
        f"| Total errors | {summary['errors']} |",
        f"| Total warnings | {summary['warnings']} |",
        "",
        "## Screens",
        "",
        "| Screen | Viewport | Status | Safe Area | Touch Targets | Spacing | Text Fit | Text Expansion | Bounds |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for row in report["matrix"]:
        lines.append(
            f"| {row['screen']} | {row['viewport']} | {row['status']} | {row['safe_area']} | "
            f"{row['touch_targets']} | {row['spacing']} | {row['text_fit']} | "
            f"{row['text_expansion']} | {row['viewport_bounds']} |"
        )
    if report["linked_reports"]:
        lines.extend(
            [
                "",
                "## Linked Reports",
                "",
                "| Area | Readiness | Source Status | Errors | Warnings | Common Rules | Top Findings | Report |",
                "|---|---|---|---:|---:|---|---|---|",
            ]
        )
        for item in report["linked_reports"]:
            lines.append(
                f"| {item['label']} | {item['readiness_status']} | {item['status']} | {item['errors']} | "
                f"{item['warnings']} | {_rule_summary(item.get('rule_summaries', []))} | "
                f"{_finding_summary(item.get('top_findings', []))} | `{item['path']}` |"
            )
    return "\n".join(lines)


def _finding_summary(findings: list[dict[str, str]]) -> str:
    if not findings:
        return "None"
    labels = []
    for finding in findings:
        location = f" ({finding['location']})" if finding.get("location") else ""
        labels.append(f"`{finding['rule']}`{location}")
    return "<br>".join(labels)


def _rule_summary(rules: list[dict[str, Any]]) -> str:
    if not rules:
        return "None"
    labels = []
    for rule in rules:
        labels.append(f"`{rule['rule']}` x{rule['findings']} ({rule['severity']})")
    return "<br>".join(labels)
