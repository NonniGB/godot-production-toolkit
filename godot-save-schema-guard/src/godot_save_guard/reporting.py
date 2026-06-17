from __future__ import annotations

import json

from . import __version__
from .models import FixtureResult
from .rule_help import catalog_for, explain_rule


def render_text_report(results: list[FixtureResult]) -> str:
    errors = _count(results, "error")
    warnings = _count(results, "warning")
    lines = [
        "Godot Save Schema Guard",
        f"Scanned {len(results)} fixture(s): {errors} error(s), {warnings} warning(s).",
    ]
    for result in results:
        for finding in result.findings:
            help_text = explain_rule(finding.rule_id)
            lines.append(f"[{finding.severity.upper()}] {result.path} {help_text['title']}: {finding.message}")
            lines.append(f"  Why it matters: {help_text['explanation']}")
    if not any(result.findings for result in results):
        lines.append("No findings.")
    return "\n".join(lines)


def render_markdown_report(results: list[FixtureResult]) -> str:
    lines = [
        "# Save Compatibility Report",
        "",
        f"Fixtures scanned: {len(results)}",
        "",
        "| Severity | Rule | Fixture | JSON Path | Message | Why It Matters |",
        "|---|---|---|---|---|---|",
    ]
    has_findings = False
    for result in results:
        for finding in result.findings:
            has_findings = True
            fixture_path = _markdown_cell(result.path.as_posix())
            help_text = explain_rule(finding.rule_id)
            lines.append(
                f"| {_markdown_cell(finding.severity)} | {_markdown_cell(finding.rule_id)} | {fixture_path} | "
                f"{_markdown_cell(finding.json_path)} | {_markdown_cell(finding.message)} | "
                f"{_markdown_cell(help_text['explanation'])} |"
            )
    if not has_findings:
        lines.append("| ok | none |  |  | No findings. |  |")
    lines.append("")
    return "\n".join(lines)


def render_json_report(results: list[FixtureResult]) -> str:
    payload = {
        "tool": "godot-save-schema-guard",
        "metadata": {
            "schema_version": "1.1",
            "tool_version": __version__,
            "report_kind": "save_schema_compatibility",
            "formats": ["text", "json", "markdown"],
        },
        "summary": {
            "fixtures": len(results),
            "findings": sum(len(result.findings) for result in results),
            "errors": _count(results, "error"),
            "warnings": _count(results, "warning"),
            "validated": _validated_count(results),
            "migrations": _rule_count(
                results,
                {
                    "migration_chain_planned",
                    "migration_command_failed",
                    "migration_compare_summary",
                    "migration_compare_unavailable",
                    "migration_output_missing",
                    "migration_path_missing",
                },
            ),
            "migration_comparisons": _rule_count(results, {"migration_compare_summary"}),
            "redacted": _rule_count(results, {"redaction_applied"}),
        },
        "rules": catalog_for({finding.rule_id for result in results for finding in result.findings}),
        "fixtures": [result.to_dict() for result in results],
    }
    return json.dumps(payload, indent=2, sort_keys=True)


def _count(results: list[FixtureResult], severity: str) -> int:
    return sum(1 for result in results for finding in result.findings if finding.severity == severity)


def _rule_count(results: list[FixtureResult], rule_ids: set[str]) -> int:
    return sum(1 for result in results for finding in result.findings if finding.rule_id in rule_ids)


def _validated_count(results: list[FixtureResult]) -> int:
    return sum(1 for result in results if not any(finding.severity == "error" for finding in result.findings))


def _markdown_cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")
