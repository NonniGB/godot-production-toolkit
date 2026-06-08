from __future__ import annotations

import json

from .models import FixtureResult


def render_text_report(results: list[FixtureResult]) -> str:
    errors = _count(results, "error")
    warnings = _count(results, "warning")
    lines = [
        "Godot Save Schema Guard",
        f"Scanned {len(results)} fixture(s): {errors} error(s), {warnings} warning(s).",
    ]
    for result in results:
        for finding in result.findings:
            lines.append(f"[{finding.severity.upper()}] {result.path} {finding.rule_id}: {finding.message}")
    if not any(result.findings for result in results):
        lines.append("No findings.")
    return "\n".join(lines)


def render_markdown_report(results: list[FixtureResult]) -> str:
    lines = [
        "# Save Compatibility Report",
        "",
        f"Fixtures scanned: {len(results)}",
        "",
        "| Severity | Rule | Fixture | JSON Path | Message |",
        "|---|---|---|---|---|",
    ]
    has_findings = False
    for result in results:
        for finding in result.findings:
            has_findings = True
            fixture_path = result.path.as_posix()
            lines.append(
                f"| {finding.severity} | {finding.rule_id} | {fixture_path} | {finding.json_path} | {finding.message} |"
            )
    if not has_findings:
        lines.append("| ok | none |  |  | No findings. |")
    lines.append("")
    return "\n".join(lines)


def render_json_report(results: list[FixtureResult]) -> str:
    payload = {
        "tool": "godot-save-schema-guard",
        "summary": {
            "fixtures": len(results),
            "findings": sum(len(result.findings) for result in results),
            "errors": _count(results, "error"),
            "warnings": _count(results, "warning"),
        },
        "fixtures": [result.to_dict() for result in results],
    }
    return json.dumps(payload, indent=2, sort_keys=True)


def _count(results: list[FixtureResult], severity: str) -> int:
    return sum(1 for result in results for finding in result.findings if finding.severity == severity)
