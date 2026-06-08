from __future__ import annotations

from pathlib import Path
from typing import Any

from godot_asset_doctor.models import ImportMetadata


def parse_import_file(path: Path) -> ImportMetadata:
    """Parse the INI-like `.import` files Godot writes next to imported assets."""
    sections: dict[str, dict[str, Any]] = {}
    current_section = ""

    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith(";") or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            current_section = line[1:-1].strip()
            sections.setdefault(current_section, {})
            continue
        if "=" not in line:
            continue

        key, raw_value = line.split("=", 1)
        section = sections.setdefault(current_section, {})
        section[key.strip()] = _coerce_value(raw_value.strip())

    return ImportMetadata(
        path=path,
        sections=sections,
        params=sections.get("params", {}),
    )


def _coerce_value(value: str) -> Any:
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        return value[1:-1]

    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False

    try:
        return int(value)
    except ValueError:
        pass

    try:
        return float(value)
    except ValueError:
        return value

