from __future__ import annotations

from dataclasses import dataclass

from .rule_help import explain_threshold, threshold_rule_id


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
        help_text = explain_threshold(self.kind)
        return {
            "rule_id": threshold_rule_id(self.kind),
            "kind": self.kind,
            "severity": self.severity,
            "title": help_text["title"],
            "explanation": help_text["explanation"],
            "message": self.message,
            "actual": self.actual,
            "expected": self.expected,
        }
