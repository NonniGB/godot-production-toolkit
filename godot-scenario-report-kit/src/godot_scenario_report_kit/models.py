from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AssertionResult:
    name: str
    status: str
    message: str = ""


@dataclass
class ScenarioResult:
    name: str
    status: str
    duration_ms: float = 0.0
    source: str = ""
    assertions: list[AssertionResult] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario": self.name,
            "status": self.status,
            "duration_ms": self.duration_ms,
            "source": self.source,
            "assertions": [assertion.__dict__ for assertion in self.assertions],
            "artifacts": self.artifacts,
        }


@dataclass
class Finding:
    rule_id: str
    severity: str
    message: str
    scenario: str | None = None
    source: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {key: value for key, value in self.__dict__.items() if value is not None}

