from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import SafeArea, Viewport


def load_visual_smoke_viewports(path: Path) -> dict[str, Viewport]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("visual smoke plan must be a JSON object.")
    commands = raw.get("commands")
    if not isinstance(commands, list):
        raise ValueError("visual smoke plan must contain a commands list.")

    viewports: dict[str, Viewport] = {}
    for index, command in enumerate(commands):
        if not isinstance(command, dict):
            raise ValueError(f"commands[{index}] must be an object.")
        viewport_raw = command.get("viewport")
        if not isinstance(viewport_raw, dict):
            raise ValueError(f"commands[{index}].viewport must be an object.")
        viewport = _viewport(viewport_raw, f"commands[{index}].viewport")
        viewports[viewport.name] = viewport
    return viewports


def merge_viewports(
    visual_smoke_viewports: dict[str, Viewport],
    metadata_viewports: dict[str, Viewport],
) -> dict[str, Viewport]:
    merged = dict(visual_smoke_viewports)
    merged.update(metadata_viewports)
    return merged


def _viewport(raw: dict[str, Any], label: str) -> Viewport:
    name = _required_str(raw, "name", label)
    return Viewport(
        name=name,
        width=_positive_int(raw.get("width"), f"{label}.width"),
        height=_positive_int(raw.get("height"), f"{label}.height"),
        safe_area=_safe_area(raw.get("safe_area", {}), f"{label}.safe_area"),
    )


def _safe_area(raw: object, label: str) -> SafeArea:
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise ValueError(f"{label} must be an object.")
    return SafeArea(
        left=_non_negative_int(raw.get("left", 0), f"{label}.left"),
        top=_non_negative_int(raw.get("top", 0), f"{label}.top"),
        right=_non_negative_int(raw.get("right", 0), f"{label}.right"),
        bottom=_non_negative_int(raw.get("bottom", 0), f"{label}.bottom"),
    )


def _required_str(raw: dict[str, Any], key: str, label: str) -> str:
    value = raw.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label}.{key} must be a non-empty string.")
    return value


def _number(value: object, label: str) -> float:
    if not isinstance(value, int | float):
        raise ValueError(f"{label} must be a number.")
    return float(value)


def _positive_int(value: object, label: str) -> int:
    number = _number(value, label)
    if number <= 0 or int(number) != number:
        raise ValueError(f"{label} must be a positive integer.")
    return int(number)


def _non_negative_int(value: object, label: str) -> int:
    number = _number(value, label)
    if number < 0 or int(number) != number:
        raise ValueError(f"{label} must be a non-negative integer.")
    return int(number)
