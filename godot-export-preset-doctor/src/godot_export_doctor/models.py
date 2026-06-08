from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ExportPreset:
    index: int
    name: str = ""
    platform: str = ""
    runnable: bool | None = None
    export_filter: str = ""
    export_path: str = ""
    options: dict[str, Any] = field(default_factory=dict)

    def display_name(self) -> str:
        return self.name or f"preset.{self.index}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "name": self.name,
            "platform": self.platform,
            "runnable": self.runnable,
            "export_filter": self.export_filter,
            "export_path": self.export_path,
            "options": self.options,
        }


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: str
    preset_index: int | None
    preset_name: str
    message: str
    option: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "preset_index": self.preset_index,
            "preset_name": self.preset_name,
            "message": self.message,
            "option": self.option,
        }
