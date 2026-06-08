from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ApiItem:
    path: str
    line: int
    kind: str
    name: str
    documented: bool
    signature: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "line": self.line,
            "kind": self.kind,
            "name": self.name,
            "documented": self.documented,
            "signature": self.signature,
        }


@dataclass(frozen=True)
class ThresholdFinding:
    kind: str
    severity: str
    message: str
    actual: float
    expected: float

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": self.kind,
            "severity": self.severity,
            "message": self.message,
            "actual": self.actual,
            "expected": self.expected,
        }
