from __future__ import annotations

from dataclasses import dataclass, field
from fnmatch import fnmatchcase
from pathlib import Path
from typing import Any
import tomllib


@dataclass(frozen=True)
class InputPolicy:
    action_groups: dict[str, list[str]] = field(default_factory=dict)
    group_requirements: dict[str, set[str]] = field(default_factory=dict)

    def group_for_action(self, action_name: str) -> str | None:
        for group, patterns in self.action_groups.items():
            if any(fnmatchcase(action_name, pattern) for pattern in patterns):
                return group
        return None

    def required_devices_for_action(self, action_name: str) -> set[str]:
        group = self.group_for_action(action_name)
        if not group:
            return set()
        return set(self.group_requirements.get(group, set()))

    def to_dict(self) -> dict[str, object]:
        return {
            "action_groups": {group: list(patterns) for group, patterns in self.action_groups.items()},
            "group_requirements": {
                group: sorted(devices) for group, devices in self.group_requirements.items()
            },
        }


def load_policy(path: Path) -> InputPolicy:
    with path.open("rb") as handle:
        data = tomllib.load(handle)
    return parse_policy(data)


def parse_policy(data: dict[str, Any]) -> InputPolicy:
    raw_groups = data.get("action_groups", {})
    raw_requirements = data.get("group_requirements", {})
    groups = {
        str(group): _string_list(patterns)
        for group, patterns in raw_groups.items()
        if _string_list(patterns)
    }
    requirements = {
        str(group): {device.strip().lower() for device in _string_list(devices) if device.strip()}
        for group, devices in raw_requirements.items()
    }
    return InputPolicy(action_groups=groups, group_requirements=requirements)


def _string_list(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value]
    return []
