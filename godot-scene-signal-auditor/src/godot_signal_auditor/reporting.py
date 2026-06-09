from __future__ import annotations

import json

from . import __version__
from .models import Finding, ParsedScene, ParsedScript
from .rule_help import catalog_for, explain_rule


def render_text_report(
    scenes: list[ParsedScene],
    scripts: dict[str, ParsedScript],
    findings: list[Finding],
) -> str:
    errors = sum(1 for finding in findings if finding.severity == "error")
    warnings = sum(1 for finding in findings if finding.severity == "warning")
    connection_count = sum(len(scene.connections) for scene in scenes)
    lines = [
        "Godot Scene Signal Auditor",
        f"Scanned {len(scenes)} scene(s), {len(scripts)} script(s), {connection_count} connection(s): {errors} error(s), {warnings} warning(s).",
    ]
    for finding in findings:
        help_text = explain_rule(finding.rule_id)
        lines.append(f"[{finding.severity.upper()}] {help_text['title']}: {finding.message}")
        lines.append(f"  Why it matters: {help_text['explanation']}")
    if not findings:
        lines.append("No findings.")
    return "\n".join(lines)


def render_json_report(
    scenes: list[ParsedScene],
    scripts: dict[str, ParsedScript],
    findings: list[Finding],
) -> str:
    payload = {
        "tool": "godot-scene-signal-auditor",
        "metadata": {
            "schema_version": "1.1",
            "tool_version": __version__,
            "report_kind": "scene_signal_audit",
            "formats": ["text", "json", "mermaid"],
        },
        "summary": {
            "scenes": len(scenes),
            "scripts": len(scripts),
            "connections": sum(len(scene.connections) for scene in scenes),
            "findings": len(findings),
            "errors": sum(1 for finding in findings if finding.severity == "error"),
            "warnings": sum(1 for finding in findings if finding.severity == "warning"),
        },
        "rules": catalog_for({finding.rule_id for finding in findings}),
        "scenes": [scene.to_dict() for scene in scenes],
        "scripts": {path: script.to_dict() for path, script in sorted(scripts.items())},
        "findings": [finding.to_dict() for finding in findings],
    }
    return json.dumps(payload, indent=2, sort_keys=True)


def render_mermaid_graph(scenes: list[ParsedScene]) -> str:
    lines = ["flowchart LR"]
    for scene in scenes:
        for connection in scene.connections:
            lines.append(
                f'  "{connection.from_node}" -->|"{connection.signal} / {connection.method}"| "{connection.to_node}"'
            )
    if len(lines) == 1:
        lines.append('  "No scene connections"')
    return "\n".join(lines) + "\n"
