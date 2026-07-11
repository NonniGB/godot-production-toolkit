from __future__ import annotations

from html import escape
import json
from pathlib import Path
from typing import Any

from . import __version__
from .loader import load_results
from .models import Finding, ScenarioResult
from .rules import enrich_finding, rule_catalog


def summarize(path: Path) -> dict[str, Any]:
    results, findings = load_results(path)
    findings.extend(_result_findings(results, path))
    return _report("summary", results, findings)


def compare(baseline: Path, current: Path, duration_ratio: float = 1.5) -> dict[str, Any]:
    baseline_results, baseline_findings = load_results(baseline)
    current_results, current_findings = load_results(current)
    findings = [*baseline_findings, *current_findings, *_result_findings(current_results, current)]
    baseline_by_name = {result.name: result for result in baseline_results}
    for result in current_results:
        previous = baseline_by_name.get(result.name)
        if not previous:
            continue
        if previous.status == "passed" and result.status != "passed":
            findings.append(
                Finding(
                    rule_id="new_scenario_failure",
                    severity="error",
                    scenario=result.name,
                    source=result.source,
                    message=f"{result.name} passed in the baseline but is now {result.status}.",
                )
            )
        if previous.duration_ms > 0 and result.duration_ms >= previous.duration_ms * duration_ratio:
            findings.append(
                Finding(
                    rule_id="duration_regression",
                    severity="warning",
                    scenario=result.name,
                    source=result.source,
                    message=(
                        f"{result.name} took {result.duration_ms:g} ms, "
                        f"up from {previous.duration_ms:g} ms."
                    ),
                )
            )
    report = _report("compare", current_results, findings)
    report["baseline"] = str(baseline)
    report["current"] = str(current)
    return report


def render(report: dict[str, Any], output_format: str) -> str:
    if output_format == "json":
        return json.dumps(report, indent=2, sort_keys=True)
    if output_format == "markdown":
        return _markdown(report)
    if output_format == "html":
        return _html(report)
    return _text(report)


def _report(kind: str, results: list[ScenarioResult], findings: list[Finding]) -> dict[str, Any]:
    enriched_findings = [enrich_finding(finding.to_dict()) for finding in findings]
    return {
        "tool": "godot-scenario-report-kit",
        "tool_version": __version__,
        "schema_version": "1.1",
        "kind": kind,
        "metadata": {
            "rules": rule_catalog(),
        },
        "summary": {
            "scenarios": len(results),
            "passed": sum(1 for result in results if result.status == "passed"),
            "failed": sum(1 for result in results if result.status == "failed"),
            "skipped": sum(1 for result in results if result.status == "skipped"),
            "warnings": sum(1 for finding in findings if finding.severity == "warning"),
            "errors": sum(1 for finding in findings if finding.severity == "error"),
            "duration_ms": sum(result.duration_ms for result in results),
        },
        "scenarios": [result.to_dict() for result in results],
        "findings": enriched_findings,
    }


def _result_findings(results: list[ScenarioResult], root: Path) -> list[Finding]:
    findings: list[Finding] = []
    base_dir = root if root.is_dir() else root.parent
    for result in results:
        if result.status == "failed":
            findings.append(
                Finding(
                    rule_id="scenario_failed",
                    severity="error",
                    scenario=result.name,
                    source=result.source,
                    message=f"{result.name} reported failed status.",
                )
            )
        for assertion in result.assertions:
            if assertion.status == "failed":
                findings.append(
                    Finding(
                        rule_id="assertion_failed",
                        severity="error",
                        scenario=result.name,
                        source=result.source,
                        message=f"{result.name} assertion {assertion.name!r} failed. {assertion.message}".strip(),
                    )
                )
        for artifact in result.artifacts:
            if not (base_dir / artifact).exists():
                findings.append(
                    Finding(
                        rule_id="missing_artifact",
                        severity="warning",
                        scenario=result.name,
                        source=result.source,
                        message=f"{result.name} lists missing artifact {artifact!r}.",
                    )
                )
    return findings


def _text(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "Godot Scenario Report Kit",
        f"Scenarios: {summary['scenarios']} passed: {summary['passed']} failed: {summary['failed']}",
        f"Findings: {summary['errors']} error(s), {summary['warnings']} warning(s).",
    ]
    for finding in report["findings"]:
        help_text = f" ({finding['rule_help']})" if finding.get("rule_help") else ""
        lines.append(f"[{finding['severity'].upper()}] {finding['rule_id']}: {finding['message']}{help_text}")
    if report.get("coverage"):
        coverage = report["coverage"]
        lines.append(
            "Coverage: "
            f"tags {len(coverage['tags'])}, "
            f"flows {len(coverage['critical_flows'])}, "
            f"platforms {len(coverage['platforms'])}."
        )
    if report.get("flake_groups"):
        lines.append(f"Flaky scenarios: {len(report['flake_groups'])}")
    if report.get("retry_groups"):
        lines.append(f"Retried scenarios: {len(report['retry_groups'])}")
    if report.get("bundle"):
        lines.append(
            "Bundle: "
            f"{summary.get('linked_evidence', 0)} linked evidence item(s), "
            f"{summary.get('artifacts', 0)} scenario artifact(s)."
        )
    return "\n".join(lines)


def _markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Godot Scenario Report",
        "",
        f"- Scenarios: {summary['scenarios']}",
        f"- Passed: {summary['passed']}",
        f"- Failed: {summary['failed']}",
        f"- Errors: {summary['errors']}",
        f"- Warnings: {summary['warnings']}",
        "",
        "| Scenario | Status | Duration ms | Assertions |",
        "|---|---|---:|---:|",
    ]
    for scenario in report["scenarios"]:
        lines.append(
            f"| {scenario['scenario']} | {scenario['status']} | {scenario['duration_ms']} | {len(scenario['assertions'])} |"
        )
    if report["findings"]:
        lines.extend(
            [
                "",
                "## Findings",
                "",
                "| Severity | Rule | Scenario | Message | Help |",
                "|---|---|---|---|---|",
            ]
        )
        for finding in report["findings"]:
            lines.append(
                f"| {finding['severity']} | {finding['rule_id']} | {finding.get('scenario', '')} | "
                f"{finding['message']} | {finding.get('rule_help', '')} |"
            )
    if report.get("coverage"):
        coverage = report["coverage"]
        lines.extend(
            [
                "",
                "## Coverage",
                "",
                "| Area | Values | Missing Required |",
                "|---|---|---|",
                f"| Tags | {', '.join(coverage['tags']) or '-'} | {', '.join(coverage['missing_required_tags']) or '-'} |",
                f"| Critical flows | {', '.join(coverage['critical_flows']) or '-'} | {', '.join(coverage['missing_required_critical_flows']) or '-'} |",
                f"| Platforms | {', '.join(coverage['platforms']) or '-'} | {', '.join(coverage['missing_required_platforms']) or '-'} |",
            ]
        )
    if report.get("flake_groups"):
        lines.extend(["", "## Flaky Scenarios", "", "| Scenario | Statuses | Observations |", "|---|---|---:|"])
        for group in report["flake_groups"]:
            lines.append(
                f"| {group['scenario']} | {', '.join(group['statuses'])} | {len(group['observations'])} |"
            )
    if report.get("retry_groups"):
        lines.extend(
            [
                "",
                "## Retried Scenarios",
                "",
                "| Scenario | Run | Attempts | Statuses | Final status |",
                "|---|---|---:|---|---|",
            ]
        )
        for group in report["retry_groups"]:
            lines.append(
                f"| {group['scenario']} | {group['run']} | {group['attempts']} | "
                f"{', '.join(group['statuses'])} | {group['final_status']} |"
            )
    if report.get("bundle"):
        lines.extend(_bundle_markdown(report["bundle"]))
    return "\n".join(lines)


def _html(report: dict[str, Any]) -> str:
    summary = report["summary"]
    scenario_rows = [
        "<tr>"
        f"<td>{escape(str(item['scenario']))}</td>"
        f"<td>{escape(str(item['status']))}</td>"
        f"<td>{item['duration_ms']}</td>"
        f"<td>{len(item['assertions'])}</td>"
        "</tr>"
        for item in report["scenarios"]
    ]
    finding_rows = [
        "<tr>"
        f"<td>{escape(str(item['severity']))}</td>"
        f"<td>{escape(str(item['rule_id']))}</td>"
        f"<td>{escape(str(item.get('scenario', '')))}</td>"
        f"<td>{escape(str(item['message']))}</td>"
        f"<td>{escape(str(item.get('rule_help', '')))}</td>"
        "</tr>"
        for item in report["findings"]
    ]
    coverage_rows: list[str] = []
    if report.get("coverage"):
        coverage = report["coverage"]
        coverage_rows = [
            "<h2>Coverage</h2><table><thead><tr><th>Area</th><th>Values</th><th>Missing required</th></tr></thead><tbody>",
            f"<tr><td>Tags</td><td>{escape(', '.join(coverage['tags']) or '-')}</td><td>{escape(', '.join(coverage['missing_required_tags']) or '-')}</td></tr>",
            f"<tr><td>Critical flows</td><td>{escape(', '.join(coverage['critical_flows']) or '-')}</td><td>{escape(', '.join(coverage['missing_required_critical_flows']) or '-')}</td></tr>",
            f"<tr><td>Platforms</td><td>{escape(', '.join(coverage['platforms']) or '-')}</td><td>{escape(', '.join(coverage['missing_required_platforms']) or '-')}</td></tr>",
            "</tbody></table>",
        ]
    flake_rows: list[str] = []
    if report.get("flake_groups"):
        flake_rows = [
            "<h2>Flaky Scenarios</h2><table><thead><tr><th>Scenario</th><th>Statuses</th><th>Observations</th></tr></thead><tbody>"
        ]
        for group in report["flake_groups"]:
            flake_rows.append(
                "<tr>"
                f"<td>{escape(str(group['scenario']))}</td>"
                f"<td>{escape(', '.join(group['statuses']))}</td>"
                f"<td>{len(group['observations'])}</td>"
                "</tr>"
            )
        flake_rows.append("</tbody></table>")
    retry_rows: list[str] = []
    if report.get("retry_groups"):
        retry_rows = [
            "<h2>Retried Scenarios</h2><table><thead><tr><th>Scenario</th><th>Run</th><th>Attempts</th><th>Statuses</th><th>Final status</th></tr></thead><tbody>"
        ]
        for group in report["retry_groups"]:
            retry_rows.append(
                "<tr>"
                f"<td>{escape(str(group['scenario']))}</td>"
                f"<td>{escape(str(group['run']))}</td>"
                f"<td>{int(group['attempts'])}</td>"
                f"<td>{escape(', '.join(group['statuses']))}</td>"
                f"<td>{escape(str(group['final_status']))}</td>"
                "</tr>"
            )
        retry_rows.append("</tbody></table>")
    bundle_rows = _bundle_html(report.get("bundle"))
    return "\n".join(
        [
            "<!doctype html>",
            "<html lang=\"en\"><head><meta charset=\"utf-8\"><title>Godot Scenario Report</title>",
            "<style>body{font-family:system-ui,sans-serif;margin:2rem;line-height:1.4;color:#182033}table{border-collapse:collapse;width:100%;margin:1rem 0}th,td{border:1px solid #d0d7de;padding:.5rem;text-align:left}th{background:#eef2f7}.metric{display:inline-block;border:1px solid #d0d7de;border-radius:8px;padding:.75rem 1rem;margin:.25rem}</style>",
            "</head><body>",
            "<h1>Godot Scenario Report</h1>",
            f"<div class=\"metric\">Scenarios: {summary['scenarios']}</div>",
            f"<div class=\"metric\">Passed: {summary['passed']}</div>",
            f"<div class=\"metric\">Failed: {summary['failed']}</div>",
            f"<div class=\"metric\">Errors: {summary['errors']}</div>",
            "<h2>Scenarios</h2><table><thead><tr><th>Scenario</th><th>Status</th><th>Duration ms</th><th>Assertions</th></tr></thead><tbody>",
            *scenario_rows,
            "</tbody></table>",
            "<h2>Findings</h2><table><thead><tr><th>Severity</th><th>Rule</th><th>Scenario</th><th>Message</th><th>Help</th></tr></thead><tbody>",
            *(finding_rows or ["<tr><td colspan=\"5\">No findings.</td></tr>"]),
            "</tbody></table>",
            *coverage_rows,
            *flake_rows,
            *retry_rows,
            *bundle_rows,
            "</body></html>",
        ]
    )


def _bundle_markdown(bundle: dict[str, Any]) -> list[str]:
    lines = ["", "## Bundle Evidence", ""]
    manifest = bundle.get("manifest_summary")
    if isinstance(manifest, dict):
        lines.extend(
            [
                "| Manifest | Value |",
                "|---|---|",
                f"| Expected scenarios | {manifest.get('expected_scenarios', 0)} |",
                f"| Result scenarios | {manifest.get('result_scenarios', 0)} |",
                f"| Missing results | {manifest.get('missing_results', 0)} |",
                f"| Unlisted results | {manifest.get('unlisted_results', 0)} |",
                f"| Missing expected artifacts | {manifest.get('missing_expected_artifacts', 0)} |",
                f"| Missing required tags | {_list_cell(manifest.get('missing_required_tags'))} |",
                f"| Missing required flows | {_list_cell(manifest.get('missing_required_critical_flows'))} |",
                f"| Missing required platforms | {_list_cell(manifest.get('missing_required_platforms'))} |",
                "",
            ]
        )
    telemetry = bundle.get("telemetry_summary")
    if isinstance(telemetry, dict):
        lines.extend(
            [
                "| Telemetry | Value |",
                "|---|---:|",
                f"| Samples | {telemetry.get('samples', 0)} |",
                f"| Frame p95 ms | {_number_cell(telemetry.get('frame_p95_ms'))} |",
                f"| Frame max ms | {_number_cell(telemetry.get('frame_max_ms'))} |",
                f"| Memory max MB | {_number_cell(telemetry.get('memory_max_mb'))} |",
                f"| Spikes | {telemetry.get('spikes', 0)} |",
                "",
            ]
        )
    visual = bundle.get("visual_summary")
    if isinstance(visual, dict):
        lines.extend(
            [
                "| Visual evidence | Value |",
                "|---|---:|",
                f"| Visual captures | {visual.get('captures', 0)} |",
                f"| Visual comparisons | {visual.get('comparisons', 0)} |",
                f"| Changed comparisons | {visual.get('changed', 0)} |",
                f"| Visual warnings | {visual.get('warnings', 0)} |",
                f"| Visual errors | {visual.get('errors', 0)} |",
                "",
            ]
        )
    log_summaries = [item for item in bundle.get("log_summaries", []) if isinstance(item, dict)]
    if log_summaries:
        lines.extend(
            [
                "| Log evidence | Value |",
                "|---|---:|",
                f"| Log files | {len(log_summaries)} |",
                f"| Log lines | {sum(int(item.get('lines', 0)) for item in log_summaries)} |",
                f"| Log warnings | {sum(int(item.get('warnings', 0)) for item in log_summaries)} |",
                f"| Log errors | {sum(int(item.get('errors', 0)) for item in log_summaries)} |",
                f"| Log crashes | {sum(int(item.get('crashes', 0)) for item in log_summaries)} |",
                "",
            ]
        )
    evidence = _bundle_evidence_rows(bundle)
    if evidence:
        lines.extend(["| Kind | Path | Exists | Size bytes |", "|---|---|---:|---:|"])
        for item in evidence:
            lines.append(
                f"| {_md_cell(item['kind'])} | {_md_cell(item['path'])} | "
                f"{str(item['exists']).lower()} | {item.get('size_bytes', '-')} |"
            )
    else:
        lines.append("No linked evidence.")

    artifact_rows = [
        {
            "scenario": row.get("scenario", ""),
            "path": artifact.get("path", ""),
            "exists": artifact.get("exists", False),
        }
        for row in bundle.get("scenarios", [])
        for artifact in row.get("bundle_artifacts", [])
    ]
    if artifact_rows:
        lines.extend(["", "## Bundle Artifacts", "", "| Scenario | Path | Exists |", "|---|---|---:|"])
        for item in artifact_rows:
            lines.append(
                f"| {_md_cell(item['scenario'])} | {_md_cell(item['path'])} | {str(item['exists']).lower()} |"
            )
    return lines


def _bundle_html(bundle: Any) -> list[str]:
    if not isinstance(bundle, dict):
        return []
    evidence = _bundle_evidence_rows(bundle)
    rows = [
        "<h2>Bundle Evidence</h2>",
        *_telemetry_summary_html(bundle.get("telemetry_summary")),
        *_manifest_summary_html(bundle.get("manifest_summary")),
        *_visual_summary_html(bundle.get("visual_summary")),
        *_log_summary_html(bundle.get("log_summaries")),
        "<table><thead><tr><th>Kind</th><th>Path</th><th>Exists</th><th>Size bytes</th></tr></thead><tbody>",
    ]
    if evidence:
        for item in evidence:
            rows.append(
                "<tr>"
                f"<td>{escape(str(item['kind']))}</td>"
                f"<td>{escape(str(item['path']))}</td>"
                f"<td>{escape(str(item['exists']).lower())}</td>"
                f"<td>{escape(str(item.get('size_bytes', '-')))}</td>"
                "</tr>"
            )
    else:
        rows.append("<tr><td colspan=\"4\">No linked evidence.</td></tr>")
    rows.append("</tbody></table>")

    artifact_rows = [
        {
            "scenario": row.get("scenario", ""),
            "path": artifact.get("path", ""),
            "exists": artifact.get("exists", False),
        }
        for row in bundle.get("scenarios", [])
        for artifact in row.get("bundle_artifacts", [])
    ]
    if artifact_rows:
        rows.append(
            "<h2>Bundle Artifacts</h2><table><thead><tr><th>Scenario</th><th>Path</th><th>Exists</th></tr></thead><tbody>"
        )
        for item in artifact_rows:
            rows.append(
                "<tr>"
                f"<td>{escape(str(item['scenario']))}</td>"
                f"<td>{escape(str(item['path']))}</td>"
                f"<td>{escape(str(item['exists']).lower())}</td>"
                "</tr>"
            )
        rows.append("</tbody></table>")
    return rows


def _bundle_evidence_rows(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    links = bundle.get("links", {})
    if isinstance(links, dict):
        for kind, item in sorted(links.items()):
            if isinstance(item, dict):
                rows.append(
                    {
                        "kind": str(item.get("kind") or kind),
                        "path": str(item.get("relative_path") or item.get("path") or ""),
                        "exists": bool(item.get("exists")),
                        **({"size_bytes": item["size_bytes"]} if "size_bytes" in item else {}),
                    }
                )
    for item in bundle.get("evidence_links", []):
        if isinstance(item, dict):
            rows.append(
                {
                    "kind": str(item.get("kind") or "evidence"),
                    "path": str(item.get("relative_path") or item.get("path") or ""),
                    "exists": bool(item.get("exists")),
                    **({"size_bytes": item["size_bytes"]} if "size_bytes" in item else {}),
                }
            )
    return rows


def _telemetry_summary_html(telemetry: Any) -> list[str]:
    if not isinstance(telemetry, dict):
        return []
    return [
        "<table><thead><tr><th>Telemetry</th><th>Value</th></tr></thead><tbody>",
        f"<tr><td>Samples</td><td>{escape(str(telemetry.get('samples', 0)))}</td></tr>",
        f"<tr><td>Frame p95 ms</td><td>{escape(_number_cell(telemetry.get('frame_p95_ms')))}</td></tr>",
        f"<tr><td>Frame max ms</td><td>{escape(_number_cell(telemetry.get('frame_max_ms')))}</td></tr>",
        f"<tr><td>Memory max MB</td><td>{escape(_number_cell(telemetry.get('memory_max_mb')))}</td></tr>",
        f"<tr><td>Spikes</td><td>{escape(str(telemetry.get('spikes', 0)))}</td></tr>",
        "</tbody></table>",
    ]


def _manifest_summary_html(manifest: Any) -> list[str]:
    if not isinstance(manifest, dict):
        return []
    rows = [
        ("Expected scenarios", manifest.get("expected_scenarios", 0)),
        ("Result scenarios", manifest.get("result_scenarios", 0)),
        ("Missing results", manifest.get("missing_results", 0)),
        ("Unlisted results", manifest.get("unlisted_results", 0)),
        ("Missing expected artifacts", manifest.get("missing_expected_artifacts", 0)),
        ("Missing required tags", _list_cell(manifest.get("missing_required_tags"))),
        ("Missing required flows", _list_cell(manifest.get("missing_required_critical_flows"))),
        ("Missing required platforms", _list_cell(manifest.get("missing_required_platforms"))),
    ]
    return [
        "<table><thead><tr><th>Manifest</th><th>Value</th></tr></thead><tbody>",
        *[
            f"<tr><td>{escape(label)}</td><td>{escape(str(value))}</td></tr>"
            for label, value in rows
        ],
        "</tbody></table>",
    ]


def _visual_summary_html(visual: Any) -> list[str]:
    if not isinstance(visual, dict):
        return []
    return [
        "<table><thead><tr><th>Visual evidence</th><th>Value</th></tr></thead><tbody>",
        f"<tr><td>Visual captures</td><td>{escape(str(visual.get('captures', 0)))}</td></tr>",
        f"<tr><td>Visual comparisons</td><td>{escape(str(visual.get('comparisons', 0)))}</td></tr>",
        f"<tr><td>Changed comparisons</td><td>{escape(str(visual.get('changed', 0)))}</td></tr>",
        f"<tr><td>Visual warnings</td><td>{escape(str(visual.get('warnings', 0)))}</td></tr>",
        f"<tr><td>Visual errors</td><td>{escape(str(visual.get('errors', 0)))}</td></tr>",
        "</tbody></table>",
    ]


def _log_summary_html(log_summaries: Any) -> list[str]:
    if not isinstance(log_summaries, list):
        return []
    rows = [item for item in log_summaries if isinstance(item, dict)]
    if not rows:
        return []
    return [
        "<table><thead><tr><th>Log evidence</th><th>Value</th></tr></thead><tbody>",
        f"<tr><td>Log files</td><td>{len(rows)}</td></tr>",
        f"<tr><td>Log lines</td><td>{sum(int(item.get('lines', 0)) for item in rows)}</td></tr>",
        f"<tr><td>Log warnings</td><td>{sum(int(item.get('warnings', 0)) for item in rows)}</td></tr>",
        f"<tr><td>Log errors</td><td>{sum(int(item.get('errors', 0)) for item in rows)}</td></tr>",
        f"<tr><td>Log crashes</td><td>{sum(int(item.get('crashes', 0)) for item in rows)}</td></tr>",
        "</tbody></table>",
    ]


def _number_cell(value: object) -> str:
    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return "0.00"


def _list_cell(value: object) -> str:
    if not isinstance(value, list):
        return "-"
    values = [str(item) for item in value if str(item).strip()]
    return _md_cell(", ".join(values) if values else "-")


def _md_cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")
