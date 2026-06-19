from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .rule_help import explain_rule


@dataclass(frozen=True)
class SceneConnection:
    scene_path: Path
    signal: str
    from_node: str
    to_node: str
    method: str

    def to_dict(self) -> dict[str, str]:
        return {
            "scene_path": self.scene_path.as_posix(),
            "signal": self.signal,
            "from_node": self.from_node,
            "to_node": self.to_node,
            "method": self.method,
        }


@dataclass(frozen=True)
class ParsedScene:
    path: Path
    node_scripts: dict[str, str] = field(default_factory=dict)
    connections: list[SceneConnection] = field(default_factory=list)
    nodes: set[str] = field(default_factory=set)
    node_groups: dict[str, set[str]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "path": self.path.as_posix(),
            "nodes": sorted(self.nodes),
            "node_scripts": self.node_scripts,
            "node_groups": {node: sorted(groups) for node, groups in sorted(self.node_groups.items())},
            "connections": [connection.to_dict() for connection in self.connections],
        }


@dataclass(frozen=True)
class ConnectCall:
    path: Path
    line: int
    signal: str
    autoload: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "path": self.path.as_posix(),
            "line": self.line,
            "signal": self.signal,
            "autoload": self.autoload,
        }


@dataclass(frozen=True)
class ParsedScript:
    path: Path
    signals: set[str]
    methods: set[str]
    connect_calls: list[ConnectCall] = field(default_factory=list)
    exported_properties: set[str] = field(default_factory=set)

    def to_dict(self) -> dict[str, object]:
        return {
            "path": self.path.as_posix(),
            "signals": sorted(self.signals),
            "methods": sorted(self.methods),
            "connect_calls": [call.to_dict() for call in self.connect_calls],
            "exported_properties": sorted(self.exported_properties),
        }


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: str
    path: Path | None
    message: str

    def to_dict(self) -> dict[str, object]:
        help_text = explain_rule(self.rule_id)
        return {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "path": self.path.as_posix() if self.path else None,
            "title": help_text["title"],
            "explanation": help_text["explanation"],
            "message": self.message,
        }
