from __future__ import annotations

from dataclasses import dataclass, field

from .rule_help import explain_rule


@dataclass(frozen=True)
class InputEvent:
    event_type: str
    device: str
    signature: str

    def to_dict(self) -> dict[str, str]:
        return {"event_type": self.event_type, "device": self.device, "signature": self.signature}


@dataclass(frozen=True)
class InputAction:
    name: str
    events: list[InputEvent] = field(default_factory=list)

    @property
    def devices(self) -> set[str]:
        return {event.device for event in self.events if event.device != "unknown"}

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "devices": sorted(self.devices),
            "events": [event.to_dict() for event in self.events],
        }


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: str
    action: str | None
    message: str

    def to_dict(self) -> dict[str, object]:
        help_text = explain_rule(self.rule_id)
        return {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "action": self.action,
            "title": help_text["title"],
            "explanation": help_text["explanation"],
            "message": self.message,
        }
