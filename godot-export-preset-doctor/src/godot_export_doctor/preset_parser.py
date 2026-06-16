from __future__ import annotations

import ast
import re
from typing import Any

from .models import ExportPreset

SECTION_RE = re.compile(r"^\[(?P<section>[^\]]+)\]$")
PRESET_RE = re.compile(r"^preset\.(?P<index>\d+)$")
OPTIONS_RE = re.compile(r"^preset\.(?P<index>\d+)\.options$")


def parse_export_presets(content: str) -> list[ExportPreset]:
    """Parse the subset of Godot's export_presets.cfg needed for validation."""
    raw_presets: dict[int, dict[str, Any]] = {}
    raw_options: dict[int, dict[str, Any]] = {}
    current_section: str | None = None

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith(";") or line.startswith("#"):
            continue

        section_match = SECTION_RE.match(line)
        if section_match:
            current_section = section_match.group("section")
            continue

        if current_section is None or "=" not in line:
            continue

        key, raw_value = line.split("=", 1)
        key = key.strip()
        value = _parse_value(raw_value.strip())

        preset_match = PRESET_RE.match(current_section)
        if preset_match:
            index = int(preset_match.group("index"))
            raw_presets.setdefault(index, {})[key] = value
            continue

        options_match = OPTIONS_RE.match(current_section)
        if options_match:
            index = int(options_match.group("index"))
            raw_options.setdefault(index, {})[key] = value

    presets: list[ExportPreset] = []
    for index in sorted(set(raw_presets) | set(raw_options)):
        fields = raw_presets.get(index, {})
        presets.append(
            ExportPreset(
                index=index,
                name=str(fields.get("name", "")),
                platform=str(fields.get("platform", "")),
                runnable=_as_optional_bool(fields.get("runnable")),
                export_filter=str(fields.get("export_filter", "")),
                include_filter=str(fields.get("include_filter", "")),
                exclude_filter=str(fields.get("exclude_filter", "")),
                custom_features=str(fields.get("custom_features", "")),
                export_path=str(fields.get("export_path", "")),
                options=raw_options.get(index, {}),
            )
        )
    return presets


def _parse_value(raw_value: str) -> Any:
    if raw_value == "true":
        return True
    if raw_value == "false":
        return False
    if re.fullmatch(r"-?\d+", raw_value):
        return int(raw_value)
    if re.fullmatch(r"-?\d+\.\d+", raw_value):
        return float(raw_value)
    if raw_value.startswith('"') and raw_value.endswith('"'):
        try:
            return ast.literal_eval(raw_value)
        except (SyntaxError, ValueError):
            return raw_value[1:-1]
    return raw_value


def _as_optional_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    return None
