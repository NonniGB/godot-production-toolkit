from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: str
    json_path: str
    message: str

    def to_dict(self) -> dict[str, object]:
        return {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "json_path": self.json_path,
            "message": self.message,
        }


@dataclass(frozen=True)
class FixtureResult:
    path: Path
    findings: list[Finding] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "path": str(self.path),
            "findings": [finding.to_dict() for finding in self.findings],
        }
