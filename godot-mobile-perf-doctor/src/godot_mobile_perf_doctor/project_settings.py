from __future__ import annotations

import ast
import re
from typing import Any

SECTION_RE = re.compile(r"^\[([^\]]+)\]$")


def parse_project_settings(content: str) -> dict[str, Any]:
    settings: dict[str, Any] = {}
    section: str | None = None
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith(";") or line.startswith("#"):
            continue
        section_match = SECTION_RE.match(line)
        if section_match:
            section = section_match.group(1)
            continue
        if section and "=" in line:
            key, value = line.split("=", 1)
            settings[f"{section}/{key.strip()}"] = _parse_value(value.strip())
    return settings


def _parse_value(raw: str) -> Any:
    if raw == "true":
        return True
    if raw == "false":
        return False
    if re.fullmatch(r"-?\d+", raw):
        return int(raw)
    if re.fullmatch(r"-?\d+\.\d+", raw):
        return float(raw)
    if raw.startswith('"') and raw.endswith('"'):
        try:
            return ast.literal_eval(raw)
        except (SyntaxError, ValueError):
            return raw.strip('"')
    return raw
