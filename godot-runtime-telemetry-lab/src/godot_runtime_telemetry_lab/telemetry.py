from __future__ import annotations

import csv
import json
from pathlib import Path
from statistics import mean
from typing import Any

from . import __version__


NUMERIC_FIELDS = ("frame_ms", "physics_ms", "memory_mb", "nodes", "draw_calls")


def summarize(path: Path, frame_budget_ms: float = 16.67) -> dict[str, Any]:
    samples = load_samples(path)
    summary = _summary(samples)
    findings = _findings(summary, frame_budget_ms)
    return {
        "tool": "godot-runtime-telemetry-lab",
        "tool_version": __version__,
        "schema_version": "1.0",
        "kind": "runtime_telemetry_summary",
        "summary": summary,
        "findings": findings,
    }


def compare(baseline: Path, current: Path, frame_budget_ms: float = 16.67, regression_ratio: float = 1.25) -> dict[str, Any]:
    baseline_report = summarize(baseline, frame_budget_ms)
    current_report = summarize(current, frame_budget_ms)
    findings = list(current_report["findings"])
    baseline_p95 = float(baseline_report["summary"]["frame_ms"]["p95"])
    current_p95 = float(current_report["summary"]["frame_ms"]["p95"])
    if baseline_p95 > 0 and current_p95 >= baseline_p95 * regression_ratio:
        findings.append(
            {
                "rule_id": "frame_p95_regression",
                "severity": "warning",
                "message": (
                    f"Frame p95 rose from {baseline_p95:.2f} ms to {current_p95:.2f} ms "
                    f"at a {regression_ratio:g}x regression threshold."
                ),
                "rule_help": "Compare recent runtime, rendering, loading, and scenario changes before updating the baseline.",
            }
        )
    return {
        "tool": "godot-runtime-telemetry-lab",
        "tool_version": __version__,
        "schema_version": "1.0",
        "kind": "runtime_telemetry_compare",
        "baseline": baseline_report["summary"],
        "current": current_report["summary"],
        "summary": {
            "errors": sum(1 for finding in findings if finding["severity"] == "error"),
            "warnings": sum(1 for finding in findings if finding["severity"] == "warning"),
            "samples": current_report["summary"]["samples"],
        },
        "findings": findings,
    }


def load_samples(path: Path) -> list[dict[str, Any]]:
    files = [path] if path.is_file() else sorted(path.glob("*.json")) + sorted(path.glob("*.csv"))
    samples: list[dict[str, Any]] = []
    for file_path in files:
        if file_path.suffix.lower() == ".csv":
            samples.extend(_load_csv(file_path))
        elif file_path.suffix.lower() == ".json":
            samples.extend(_load_json(file_path))
    return samples


def render(report: dict[str, Any], output_format: str) -> str:
    if output_format == "json":
        return json.dumps(report, indent=2, sort_keys=True)
    if output_format == "markdown":
        return _markdown(report)
    return _text(report)


def _load_json(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        for key in ("samples", "frames", "events"):
            value = data.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
        return [data]
    return []


def _load_csv(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _summary(samples: list[dict[str, Any]]) -> dict[str, Any]:
    scenarios = sorted({str(sample.get("scenario", "default")) for sample in samples})
    return {
        "samples": len(samples),
        "scenarios": scenarios,
        "errors": 0,
        "warnings": 0,
        **{field: _metric(samples, field) for field in NUMERIC_FIELDS},
    }


def _metric(samples: list[dict[str, Any]], field: str) -> dict[str, float]:
    values = sorted(_number(sample.get(field)) for sample in samples if _number(sample.get(field)) is not None)
    if not values:
        return {"min": 0.0, "avg": 0.0, "p95": 0.0, "max": 0.0}
    return {
        "min": values[0],
        "avg": mean(values),
        "p95": _percentile(values, 0.95),
        "max": values[-1],
    }


def _findings(summary: dict[str, Any], frame_budget_ms: float) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    p95 = float(summary["frame_ms"]["p95"])
    if p95 > frame_budget_ms:
        findings.append(
            {
                "rule_id": "frame_p95_over_budget",
                "severity": "warning",
                "message": f"Frame p95 is {p95:.2f} ms, above the {frame_budget_ms:g} ms budget.",
                "rule_help": "Inspect scenario phases and recent rendering or script changes around the slow frames.",
            }
        )
    return findings


def _number(value: object) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _percentile(values: list[float], fraction: float) -> float:
    if len(values) == 1:
        return values[0]
    index = round((len(values) - 1) * fraction)
    return values[index]


def _text(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "Godot Runtime Telemetry Lab",
        f"Samples: {summary['samples']} | Errors: {summary['errors']} | Warnings: {summary['warnings']}",
        f"Frame p95: {summary['frame_ms']['p95']:.2f} ms | max: {summary['frame_ms']['max']:.2f} ms",
    ]
    for finding in report["findings"]:
        lines.append(f"- {finding['severity'].upper()} {finding['rule_id']}: {finding['message']}")
    return "\n".join(lines)


def _markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Godot Runtime Telemetry",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Samples | {summary['samples']} |",
        f"| Frame p95 ms | {summary['frame_ms']['p95']:.2f} |",
        f"| Frame max ms | {summary['frame_ms']['max']:.2f} |",
        f"| Warnings | {summary['warnings']} |",
        "",
        "## Findings",
        "",
    ]
    if not report["findings"]:
        lines.append("No telemetry findings.")
    else:
        lines.extend(["| Severity | Rule | Message |", "|---|---|---|"])
        for finding in report["findings"]:
            lines.append(f"| {finding['severity']} | `{finding['rule_id']}` | {finding['message']} |")
    return "\n".join(lines)
