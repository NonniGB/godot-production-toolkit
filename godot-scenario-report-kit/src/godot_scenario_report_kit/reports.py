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
            "</tbody></table></body></html>",
        ]
    )
