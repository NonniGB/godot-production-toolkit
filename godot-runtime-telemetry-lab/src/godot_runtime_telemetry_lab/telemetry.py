from __future__ import annotations

import csv
from html import escape
import json
from pathlib import Path
from statistics import mean
from typing import Any

from . import __version__


NUMERIC_FIELDS = ("frame_ms", "physics_ms", "memory_mb", "nodes", "draw_calls")

BUDGET_PROFILES: dict[str, dict[str, Any]] = {
    "desktop-dev": {
        "frame_budget_ms": 16.67,
        "memory_budget_mb": 1024,
        "description": "Local desktop development target for ordinary gameplay scenes.",
    },
    "android-high": {
        "frame_budget_ms": 16.67,
        "memory_budget_mb": 768,
        "description": "High-end Android target where 60 fps is expected.",
    },
    "android-low": {
        "frame_budget_ms": 33.33,
        "memory_budget_mb": 512,
        "description": "Lower-end Android target where stable 30 fps is acceptable.",
    },
    "html5": {
        "frame_budget_ms": 33.33,
        "memory_budget_mb": 512,
        "description": "Browser export target with a conservative frame budget.",
    },
}


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


def compare(
    baseline: Path,
    current: Path,
    frame_budget_ms: float = 16.67,
    regression_ratio: float = 1.25,
) -> dict[str, Any]:
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


def timeline(path: Path, frame_budget_ms: float = 16.67, memory_budget_mb: float | None = None) -> dict[str, Any]:
    samples = load_samples(path)
    samples = _sorted_samples(samples)
    spikes = _spikes(samples, frame_budget_ms, memory_budget_mb)
    return {
        "tool": "godot-runtime-telemetry-lab",
        "tool_version": __version__,
        "schema_version": "1.0",
        "kind": "runtime_telemetry_timeline",
        "summary": {
            **_summary(samples),
            "frame_budget_ms": frame_budget_ms,
            "memory_budget_mb": memory_budget_mb,
            "phases": _phases(samples),
            "spikes": len(spikes),
        },
        "samples": [_timeline_sample(sample, index) for index, sample in enumerate(samples)],
        "spikes": spikes,
        "findings": _findings(_summary(samples), frame_budget_ms),
    }


def budget_profile(name: str) -> dict[str, Any]:
    if name not in BUDGET_PROFILES:
        valid = ", ".join(sorted(BUDGET_PROFILES))
        raise ValueError(f"Unknown budget profile '{name}'. Valid profiles: {valid}.")
    return {
        "tool": "godot-runtime-telemetry-lab",
        "tool_version": __version__,
        "schema_version": "1.0",
        "kind": "runtime_telemetry_budget",
        "profile": name,
        **BUDGET_PROFILES[name],
    }


def adapt(path: Path, source_format: str = "auto") -> dict[str, Any]:
    raw_samples = load_samples(path)
    samples = [_adapt_sample(sample, index) for index, sample in enumerate(raw_samples)]
    return {
        "tool": "godot-runtime-telemetry-lab",
        "tool_version": __version__,
        "schema_version": "1.0",
        "kind": "runtime_telemetry_adapter",
        "source_format": source_format,
        "summary": {
            "samples": len(samples),
            "scenarios": sorted({str(sample.get("scenario", "default")) for sample in samples}),
            "errors": 0,
            "warnings": 0,
        },
        "samples": samples,
        "findings": [],
    }


def load_budget(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Budget file must contain a JSON object.")
    return data


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
    if output_format == "html":
        return _timeline_html(report)
    if output_format == "svg":
        return _timeline_svg(report)
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


def _adapt_sample(sample: dict[str, Any], index: int) -> dict[str, Any]:
    fps = _first_number(sample, "fps", "frames_per_second", "Performance.TIME_FPS")
    frame_ms = _first_number(
        sample,
        "frame_ms",
        "frame_time_ms",
        "delta_ms",
        "process_ms",
    )
    performance_process_s = _first_number(sample, "Performance.TIME_PROCESS")
    if frame_ms is None and performance_process_s is not None:
        frame_ms = performance_process_s * 1000.0
    if frame_ms is None and fps and fps > 0:
        frame_ms = 1000.0 / fps
    physics_ms = _first_number(sample, "physics_ms", "physics_frame_ms", "physics_process_ms")
    performance_physics_s = _first_number(sample, "Performance.TIME_PHYSICS_PROCESS")
    if physics_ms is None and performance_physics_s is not None:
        physics_ms = performance_physics_s * 1000.0
    memory_mb = _first_number(
        sample,
        "memory_mb",
        "static_memory_mb",
        "memory_static_mb",
        "Performance.MEMORY_STATIC",
        "Performance.RENDER_VIDEO_MEM_USED",
        "Performance.RENDER_TEXTURE_MEM_USED",
        "Performance.RENDER_BUFFER_MEM_USED",
    )
    if memory_mb is not None and memory_mb > 4096:
        memory_mb = memory_mb / 1048576.0
    return {
        "scenario": str(sample.get("scenario") or sample.get("run") or "default"),
        "phase": str(sample.get("phase") or sample.get("event") or ""),
        "time_s": _first_number(sample, "time_s", "timestamp_s", "elapsed_s", "time") or float(index),
        "frame": _first_number(sample, "frame", "frame_index") or index,
        "frame_ms": frame_ms or 0.0,
        "physics_ms": physics_ms or 0.0,
        "memory_mb": memory_mb or 0.0,
        "nodes": int(_first_number(sample, "nodes", "node_count", "object_node_count", "Performance.OBJECT_NODE_COUNT") or 0),
        "draw_calls": int(_first_number(sample, "draw_calls", "render_draw_calls", "Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME") or 0),
    }


def _first_number(sample: dict[str, Any], *keys: str) -> float | None:
    lowered = {str(key).lower(): value for key, value in sample.items()}
    for key in keys:
        value = sample.get(key)
        if value is None:
            value = lowered.get(key.lower())
        number = _number(value)
        if number is not None:
            return number
    return None


def _summary(samples: list[dict[str, Any]]) -> dict[str, Any]:
    scenarios = sorted({str(sample.get("scenario", "default")) for sample in samples})
    return {
        "samples": len(samples),
        "scenarios": scenarios,
        "errors": 0,
        "warnings": 0,
        **{field: _metric(samples, field) for field in NUMERIC_FIELDS},
    }


def _sorted_samples(samples: list[dict[str, Any]]) -> list[dict[str, Any]]:
    def key(sample: dict[str, Any]) -> tuple[float, str]:
        timestamp = _number(sample.get("time_s"))
        if timestamp is None:
            timestamp = _number(sample.get("timestamp_s"))
        if timestamp is None:
            timestamp = _number(sample.get("frame"))
        return (timestamp if timestamp is not None else float("inf"), str(sample.get("scenario", "")))

    return sorted(samples, key=key)


def _timeline_sample(sample: dict[str, Any], index: int) -> dict[str, Any]:
    return {
        "index": index,
        "time_s": _number(sample.get("time_s")) or _number(sample.get("timestamp_s")) or float(index),
        "frame": _number(sample.get("frame")) or index,
        "scenario": str(sample.get("scenario", "default")),
        "phase": str(sample.get("phase", sample.get("event", ""))),
        "frame_ms": _number(sample.get("frame_ms")) or 0.0,
        "physics_ms": _number(sample.get("physics_ms")) or 0.0,
        "memory_mb": _number(sample.get("memory_mb")) or 0.0,
    }


def _spikes(
    samples: list[dict[str, Any]], frame_budget_ms: float, memory_budget_mb: float | None
) -> list[dict[str, Any]]:
    spikes: list[dict[str, Any]] = []
    for index, sample in enumerate(samples):
        timeline_sample = _timeline_sample(sample, index)
        if timeline_sample["frame_ms"] > frame_budget_ms:
            spikes.append(
                {
                    **timeline_sample,
                    "rule_id": "frame_over_budget",
                    "severity": "warning",
                    "message": f"Frame time {timeline_sample['frame_ms']:.2f} ms exceeded {frame_budget_ms:g} ms.",
                }
            )
        if memory_budget_mb is not None and timeline_sample["memory_mb"] > memory_budget_mb:
            spikes.append(
                {
                    **timeline_sample,
                    "rule_id": "memory_over_budget",
                    "severity": "warning",
                    "message": f"Memory {timeline_sample['memory_mb']:.1f} MB exceeded {memory_budget_mb:g} MB.",
                }
            )
    return spikes


def _phases(samples: list[dict[str, Any]]) -> list[dict[str, Any]]:
    phases: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for index, sample in enumerate(samples):
        timeline_sample = _timeline_sample(sample, index)
        phase = timeline_sample["phase"] or timeline_sample["scenario"]
        if current is None or current["name"] != phase:
            if current is not None:
                phases.append(current)
            current = {"name": phase, "start_index": index, "end_index": index}
        else:
            current["end_index"] = index
    if current is not None:
        phases.append(current)
    return phases


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
    if report.get("kind") == "runtime_telemetry_adapter":
        return f"Godot Runtime Telemetry Adapter\nSamples: {summary['samples']}"
    if report.get("kind") == "runtime_telemetry_timeline":
        return _timeline_text(report)
    if report.get("kind") == "runtime_telemetry_budget":
        return _budget_text(report)
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
    if report.get("kind") == "runtime_telemetry_adapter":
        return "\n".join(["# Godot Runtime Telemetry Adapter", "", f"- Samples: {summary['samples']}"])
    if report.get("kind") == "runtime_telemetry_timeline":
        return _timeline_markdown(report)
    if report.get("kind") == "runtime_telemetry_budget":
        return _budget_markdown(report)
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


def _budget_text(report: dict[str, Any]) -> str:
    return (
        f"{report['profile']}: frame {report['frame_budget_ms']:g} ms, "
        f"memory {report['memory_budget_mb']:g} MB"
    )


def _budget_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"# Runtime Budget: {report['profile']}",
            "",
            f"- Frame budget: {report['frame_budget_ms']:g} ms",
            f"- Memory budget: {report['memory_budget_mb']:g} MB",
            f"- Notes: {report['description']}",
        ]
    )


def _timeline_text(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "Godot Runtime Telemetry Timeline",
        f"Samples: {summary['samples']} | Spikes: {summary['spikes']} | Budget: {summary['frame_budget_ms']:g} ms",
        f"Frame p95: {summary['frame_ms']['p95']:.2f} ms | max: {summary['frame_ms']['max']:.2f} ms",
    ]
    for spike in report["spikes"][:10]:
        lines.append(
            f"- {spike['rule_id']} at sample {spike['index']} ({spike['scenario']}): {spike['message']}"
        )
    return "\n".join(lines)


def _timeline_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Godot Runtime Telemetry Timeline",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Samples | {summary['samples']} |",
        f"| Frame budget ms | {summary['frame_budget_ms']:g} |",
        f"| Frame p95 ms | {summary['frame_ms']['p95']:.2f} |",
        f"| Frame max ms | {summary['frame_ms']['max']:.2f} |",
        f"| Spikes | {summary['spikes']} |",
        "",
        "## Spikes",
        "",
    ]
    if not report["spikes"]:
        lines.append("No timeline spikes.")
    else:
        lines.extend(["| Sample | Scenario | Phase | Rule | Message |", "|---:|---|---|---|---|"])
        for spike in report["spikes"][:25]:
            lines.append(
                f"| {spike['index']} | {spike['scenario']} | {spike['phase']} | "
                f"`{spike['rule_id']}` | {spike['message']} |"
            )
    return "\n".join(lines)


def _timeline_html(report: dict[str, Any]) -> str:
    summary = report["summary"]
    chart = _timeline_svg(report, embedded=True)
    spike_rows = "\n".join(
        "<tr>"
        f"<td>{spike['index']}</td>"
        f"<td>{escape(str(spike['scenario']))}</td>"
        f"<td>{escape(str(spike['phase']))}</td>"
        f"<td>{escape(str(spike['rule_id']))}</td>"
        f"<td>{escape(str(spike['message']))}</td>"
        "</tr>"
        for spike in report["spikes"][:50]
    )
    if not spike_rows:
        spike_rows = '<tr><td colspan="5">No spikes over the selected budgets.</td></tr>'
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Godot Runtime Telemetry Timeline</title>
  <style>
    body {{ margin: 0; font-family: Arial, sans-serif; color: #172026; background: #f6f8fb; }}
    main {{ max-width: 1080px; margin: 0 auto; padding: 32px 20px 48px; }}
    h1 {{ margin: 0 0 8px; font-size: 30px; }}
    .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin: 22px 0; }}
    .metric {{ background: white; border: 1px solid #d9e0ea; border-radius: 8px; padding: 14px; }}
    .metric strong {{ display: block; font-size: 24px; margin-bottom: 4px; }}
    .chart {{ background: white; border: 1px solid #d9e0ea; border-radius: 8px; padding: 16px; overflow-x: auto; }}
    table {{ width: 100%; margin-top: 24px; border-collapse: collapse; background: white; border: 1px solid #d9e0ea; }}
    th, td {{ text-align: left; padding: 10px 12px; border-bottom: 1px solid #e6ebf2; font-size: 14px; }}
    th {{ background: #eef3f9; }}
  </style>
</head>
<body>
<main>
  <h1>Godot Runtime Telemetry Timeline</h1>
  <p>Frame, memory, and scenario-phase evidence from lightweight JSON or CSV runtime samples.</p>
  <section class="summary">
    <div class="metric"><strong>{summary['samples']}</strong>samples</div>
    <div class="metric"><strong>{summary['spikes']}</strong>budget spikes</div>
    <div class="metric"><strong>{summary['frame_ms']['p95']:.2f} ms</strong>frame p95</div>
    <div class="metric"><strong>{summary['frame_ms']['max']:.2f} ms</strong>frame max</div>
  </section>
  <section class="chart">{chart}</section>
  <table>
    <thead><tr><th>Sample</th><th>Scenario</th><th>Phase</th><th>Rule</th><th>Message</th></tr></thead>
    <tbody>{spike_rows}</tbody>
  </table>
</main>
</body>
</html>"""


def _timeline_svg(report: dict[str, Any], embedded: bool = False) -> str:
    samples = report.get("samples", [])
    summary = report["summary"]
    width = max(720, min(1320, 60 + len(samples) * 22))
    height = 320
    left = 48
    top = 38
    chart_width = width - 80
    chart_height = 190
    max_frame = max(float(summary["frame_ms"]["max"]), float(summary["frame_budget_ms"]), 1.0)
    points = []
    markers = []
    for index, sample in enumerate(samples):
        x = left + (chart_width * index / max(1, len(samples) - 1))
        y = top + chart_height - (chart_height * float(sample["frame_ms"]) / max_frame)
        points.append(f"{x:.1f},{y:.1f}")
        if float(sample["frame_ms"]) > float(summary["frame_budget_ms"]):
            markers.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="#d64550">'
                f'<title>Sample {sample["index"]}: {sample["frame_ms"]:.2f} ms</title></circle>'
            )
    budget_y = top + chart_height - (chart_height * float(summary["frame_budget_ms"]) / max_frame)
    polyline = " ".join(points)
    markers_html = "\n  ".join(markers)
    title = "" if embedded else "<title>Godot Runtime Telemetry Timeline</title>"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Godot runtime telemetry timeline">
  {title}
  <rect width="100%" height="100%" fill="#ffffff"/>
  <text x="{left}" y="24" font-family="Arial, sans-serif" font-size="18" font-weight="700" fill="#172026">Frame time timeline</text>
  <line x1="{left}" y1="{budget_y:.1f}" x2="{left + chart_width}" y2="{budget_y:.1f}" stroke="#f0a000" stroke-width="2" stroke-dasharray="6 5"/>
  <text x="{left + chart_width - 110}" y="{max(16, budget_y - 8):.1f}" font-family="Arial, sans-serif" font-size="12" fill="#7a5400">budget {summary['frame_budget_ms']:g} ms</text>
  <line x1="{left}" y1="{top}" x2="{left}" y2="{top + chart_height}" stroke="#8190a0"/>
  <line x1="{left}" y1="{top + chart_height}" x2="{left + chart_width}" y2="{top + chart_height}" stroke="#8190a0"/>
  <polyline points="{polyline}" fill="none" stroke="#2457c5" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>
  {markers_html}
  <text x="{left}" y="{height - 54}" font-family="Arial, sans-serif" font-size="13" fill="#374151">Samples: {summary['samples']} | Spikes: {summary['spikes']} | p95: {summary['frame_ms']['p95']:.2f} ms | max: {summary['frame_ms']['max']:.2f} ms</text>
  <text x="{left}" y="{height - 30}" font-family="Arial, sans-serif" font-size="12" fill="#5f6b7a">Red markers show samples over the selected frame budget.</text>
</svg>"""
