from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ModulePolicy:
    name: str
    paths: tuple[str, ...]
    may_depend_on: tuple[str, ...]
    allowed_autoloads: tuple[str, ...]


@dataclass
class Finding:
    rule_id: str
    severity: str
    message: str
    path: str | None = None
    module: str | None = None
    target: str | None = None
    line: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {key: value for key, value in self.__dict__.items() if value is not None}

