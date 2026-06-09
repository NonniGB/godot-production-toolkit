from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SafeArea:
    left: int = 0
    top: int = 0
    right: int = 0
    bottom: int = 0


@dataclass(frozen=True)
class Viewport:
    name: str
    width: int
    height: int
    safe_area: SafeArea = field(default_factory=SafeArea)


@dataclass(frozen=True)
class UiNode:
    id: str
    kind: str
    x: float
    y: float
    width: float
    height: float
    text: str = ""
    font_size: float = 16.0
    interactive: bool = False


@dataclass(frozen=True)
class Screen:
    name: str
    viewport: str
    nodes: list[UiNode]


@dataclass(frozen=True)
class Thresholds:
    min_touch_size: int = 44
    min_touch_spacing: int = 8
    max_text_width_ratio: float = 0.95


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: str
    message: str
    screen: str | None = None
    node: str | None = None
    viewport: str | None = None
    help: str = ""

    def as_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "message": self.message,
        }
        if self.screen:
            result["screen"] = self.screen
        if self.node:
            result["node"] = self.node
        if self.viewport:
            result["viewport"] = self.viewport
        if self.help:
            result["help"] = self.help
        return result
