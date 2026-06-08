from __future__ import annotations

import json

from .models import Finding, ParsedScene, ParsedScript


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
        lines.append(f"[{finding.severity.upper()}] {finding.rule_id}: {finding.message}")
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
        "summary": {
            "scenes": len(scenes),
            "scripts": len(scripts),
            "connections": sum(len(scene.connections) for scene in scenes),
            "findings": len(findings),
            "errors": sum(1 for finding in findings if finding.severity == "error"),
            "warnings": sum(1 for finding in findings if finding.severity == "warning"),
        },
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
