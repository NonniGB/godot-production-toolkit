from __future__ import annotations

from pathlib import Path

from .models import Finding, ParsedScene, ParsedScript


def audit_project_model(
    scenes: list[ParsedScene],
    scripts: dict[str, ParsedScript],
    *,
    strict_stale_connections: bool,
) -> list[Finding]:
    findings: list[Finding] = []
    for scene in scenes:
        for connection in scene.connections:
            script_path = scene.node_scripts.get(connection.to_node)
            if not script_path:
                continue
            target_script = scripts.get(script_path)
            if not target_script:
                continue
            if connection.method not in target_script.methods:
                severity = "error" if strict_stale_connections else "warning"
                findings.append(
                    Finding(
                        "stale_scene_connection",
                        severity,
                        scene.path,
                        (
                            f"Connection from '{connection.from_node}' signal '{connection.signal}' "
                            f"targets missing method '{connection.method}' in {script_path}."
                        ),
                    )
                )

    for script in scripts.values():
        for call in script.connect_calls:
            if call.autoload:
                findings.append(
                    Finding(
                        "autoload_signal_usage",
                        "warning",
                        Path(call.path),
                        f"Autoload '{call.autoload}' signal '{call.signal}' is connected at line {call.line}.",
                    )
                )
    return findings
