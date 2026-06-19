from __future__ import annotations

import fnmatch
import json
import tomllib
from pathlib import Path
from typing import Any

from .models import Finding, ParsedScene, ParsedScript


def load_contract(path: Path) -> dict[str, Any]:
    content = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".toml":
        return tomllib.loads(content)
    return json.loads(content)


def audit_scene_contracts(
    scenes: list[ParsedScene],
    scripts: dict[str, ParsedScript],
    contract: dict[str, Any],
) -> list[Finding]:
    findings: list[Finding] = []
    scene_specs = _scene_specs(contract)
    scenes_by_path = {scene.path.as_posix(): scene for scene in scenes}

    for spec in scene_specs:
        path = _string_value(spec, "path")
        pattern = _string_value(spec, "path_pattern")
        matched_scenes = _matching_scenes(scenes, scenes_by_path, path, pattern)
        if not matched_scenes:
            label = path or pattern or "<unspecified>"
            findings.append(
                Finding(
                    "scene_contract_violation",
                    "error",
                    Path(label) if label != "<unspecified>" else None,
                    f"Scene contract target '{label}' did not match any scanned scene.",
                )
            )
            continue

        for scene in matched_scenes:
            findings.extend(_audit_scene_spec(scene, scripts, spec))

    return findings


def _scene_specs(contract: dict[str, Any]) -> list[dict[str, Any]]:
    raw_scenes = contract.get("scenes", [])
    if isinstance(raw_scenes, dict):
        specs: list[dict[str, Any]] = []
        for scene_path, spec in raw_scenes.items():
            if isinstance(spec, dict):
                specs.append({"path": scene_path, **spec})
        return specs
    if isinstance(raw_scenes, list):
        return [spec for spec in raw_scenes if isinstance(spec, dict)]
    return []


def _matching_scenes(
    scenes: list[ParsedScene],
    scenes_by_path: dict[str, ParsedScene],
    path: str | None,
    pattern: str | None,
) -> list[ParsedScene]:
    if path:
        scene = scenes_by_path.get(path)
        return [scene] if scene else []
    if pattern:
        return [
            scene
            for scene in scenes
            if fnmatch.fnmatch(scene.path.as_posix(), pattern)
        ]
    return []


def _audit_scene_spec(
    scene: ParsedScene,
    scripts: dict[str, ParsedScript],
    spec: dict[str, Any],
) -> list[Finding]:
    findings: list[Finding] = []
    for node in _string_list(spec.get("required_nodes")):
        if node not in scene.nodes:
            findings.append(
                _contract_finding(
                    scene.path,
                    f"Scene '{scene.path.as_posix()}' is missing required node '{node}'.",
                )
            )

    required_connections = spec.get("required_connections", spec.get("expected_connections", []))
    for connection in _connection_specs(required_connections):
        if not _has_connection(scene, connection):
            message = (
                f"Scene '{scene.path.as_posix()}' is missing required connection "
                f"'{connection['from']}.{connection['signal']} -> {_target_label(connection)}'."
            )
            findings.append(_contract_finding(scene.path, message))

    findings.extend(_audit_script_members(scene, scripts, spec.get("script_methods"), "method"))
    findings.extend(_audit_script_members(scene, scripts, spec.get("script_signals"), "signal"))
    findings.extend(_audit_node_groups(scene, _first_mapping(spec, "node_groups", "required_groups")))
    findings.extend(
        _audit_script_members(
            scene,
            scripts,
            _first_mapping(
                spec,
                "script_exports",
                "script_exported_properties",
                "exported_properties",
            ),
            "exported property",
        )
    )
    return findings


def _audit_script_members(
    scene: ParsedScene,
    scripts: dict[str, ParsedScript],
    raw_members: object,
    member_kind: str,
) -> list[Finding]:
    findings: list[Finding] = []
    if not isinstance(raw_members, dict):
        return findings

    for node, names in raw_members.items():
        if not isinstance(node, str):
            continue
        script_path = scene.node_scripts.get(node)
        if not script_path:
            findings.append(
                _contract_finding(
                    scene.path,
                    (
                        f"Node '{node}' in scene '{scene.path.as_posix()}' has no script "
                        f"for required {member_kind} contract."
                    ),
                )
            )
            continue

        script = scripts.get(script_path)
        if not script:
            available: set[str] = set()
        elif member_kind == "method":
            available = script.methods
        elif member_kind == "signal":
            available = script.signals
        else:
            available = script.exported_properties
        for name in _string_list(names):
            if name not in available:
                findings.append(
                    _contract_finding(
                        scene.path,
                        (
                            f"Script '{script_path}' for node '{node}' "
                            f"in scene '{scene.path.as_posix()}' "
                            f"is missing required {member_kind} '{name}'."
                        ),
                    )
                )
    return findings


def _audit_node_groups(scene: ParsedScene, raw_groups: object) -> list[Finding]:
    findings: list[Finding] = []
    if not isinstance(raw_groups, dict):
        return findings
    for node, group_names in raw_groups.items():
        if not isinstance(node, str):
            continue
        if node not in scene.nodes:
            findings.append(
                _contract_finding(
                    scene.path,
                    f"Scene '{scene.path.as_posix()}' is missing required node '{node}'.",
                )
            )
            continue
        available = scene.node_groups.get(node, set())
        for group_name in _string_list(group_names):
            if group_name not in available:
                findings.append(
                    _contract_finding(
                        scene.path,
                        f"Node '{node}' in scene '{scene.path.as_posix()}' is missing required group '{group_name}'.",
                    )
                )
    return findings


def _has_connection(scene: ParsedScene, expected: dict[str, str]) -> bool:
    return any(
        connection.from_node == expected["from"]
        and connection.signal == expected["signal"]
        and connection.to_node == expected["to"]
        and connection.method == expected["method"]
        for connection in scene.connections
    )


def _target_label(connection: dict[str, str]) -> str:
    if connection["to"] == ".":
        return f".{connection['method']}"
    return f"{connection['to']}.{connection['method']}"


def _connection_specs(raw_connections: object) -> list[dict[str, str]]:
    specs: list[dict[str, str]] = []
    if not isinstance(raw_connections, list):
        return specs
    for raw_connection in raw_connections:
        if not isinstance(raw_connection, dict):
            continue
        from_node = raw_connection.get("from", raw_connection.get("from_node"))
        to_node = raw_connection.get("to", raw_connection.get("to_node"))
        signal = raw_connection.get("signal")
        method = raw_connection.get("method")
        if all(isinstance(value, str) for value in [from_node, signal, to_node, method]):
            specs.append(
                {"from": from_node, "signal": signal, "to": to_node, "method": method}
            )
    return specs


def _string_value(raw: dict[str, Any], key: str) -> str | None:
    value = raw.get(key)
    return value if isinstance(value, str) else None


def _string_list(raw: object) -> list[str]:
    if not isinstance(raw, list):
        return []
    return [value for value in raw if isinstance(value, str)]


def _first_mapping(raw: dict[str, Any], *keys: str) -> object:
    for key in keys:
        value = raw.get(key)
        if isinstance(value, dict):
            return value
    return None


def _contract_finding(path: Path, message: str) -> Finding:
    return Finding("scene_contract_violation", "error", path, message)
