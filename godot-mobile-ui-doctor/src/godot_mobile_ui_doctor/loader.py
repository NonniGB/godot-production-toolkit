from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import SafeArea, Screen, Thresholds, UiNode, Viewport


def load_metadata(path: Path) -> tuple[dict[str, Viewport], list[Screen], Thresholds]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("UI metadata must be a JSON object.")

    thresholds = _load_thresholds(raw.get("thresholds", {}))
    viewports = _load_viewports(raw)
    screens = _load_screens(raw)
    return viewports, screens, thresholds


def _load_thresholds(raw: object) -> Thresholds:
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise ValueError("thresholds must be an object when provided.")
    return Thresholds(
        min_touch_size=_positive_int(raw.get("min_touch_size", 44), "thresholds.min_touch_size"),
        min_touch_spacing=_positive_int(
            raw.get("min_touch_spacing", 8), "thresholds.min_touch_spacing"
        ),
        max_text_width_ratio=_positive_float(
            raw.get("max_text_width_ratio", 0.95), "thresholds.max_text_width_ratio"
        ),
    )


def _load_viewports(raw: dict[str, Any]) -> dict[str, Viewport]:
    viewports_raw = raw.get("viewports")
    if not isinstance(viewports_raw, list) or not viewports_raw:
        raise ValueError("viewports must be a non-empty list.")

    viewports: dict[str, Viewport] = {}
    for index, item in enumerate(viewports_raw):
        if not isinstance(item, dict):
            raise ValueError(f"viewports[{index}] must be an object.")
        name = _required_str(item, "name", f"viewports[{index}]")
        viewports[name] = Viewport(
            name=name,
            width=_positive_int(item.get("width"), f"viewports[{index}].width"),
            height=_positive_int(item.get("height"), f"viewports[{index}].height"),
            safe_area=_safe_area(item.get("safe_area", {}), f"viewports[{index}].safe_area"),
        )
    return viewports


def _load_screens(raw: dict[str, Any]) -> list[Screen]:
    screens_raw = raw.get("screens")
    if not isinstance(screens_raw, list) or not screens_raw:
        raise ValueError("screens must be a non-empty list.")

    screens: list[Screen] = []
    for screen_index, item in enumerate(screens_raw):
        if not isinstance(item, dict):
            raise ValueError(f"screens[{screen_index}] must be an object.")
        screen_label = f"screens[{screen_index}]"
        nodes_raw = item.get("nodes", [])
        if not isinstance(nodes_raw, list):
            raise ValueError(f"{screen_label}.nodes must be a list.")
        nodes = [
            _node(node, f"{screen_label}.nodes[{node_index}]")
            for node_index, node in enumerate(nodes_raw)
        ]
        screens.append(
            Screen(
                name=_required_str(item, "name", screen_label),
                viewport=_required_str(item, "viewport", screen_label),
                nodes=nodes,
            )
        )
    return screens


def _node(raw: object, label: str) -> UiNode:
    if not isinstance(raw, dict):
        raise ValueError(f"{label} must be an object.")
    return UiNode(
        id=_required_str(raw, "id", label),
        kind=str(raw.get("kind", raw.get("type", "control"))),
        x=_number(raw.get("x"), f"{label}.x"),
        y=_number(raw.get("y"), f"{label}.y"),
        width=_positive_float(raw.get("width"), f"{label}.width"),
        height=_positive_float(raw.get("height"), f"{label}.height"),
        text=str(raw.get("text", "")),
        font_size=_positive_float(raw.get("font_size", 16), f"{label}.font_size"),
        interactive=bool(raw.get("interactive", False)),
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


def _positive_float(value: object, label: str) -> float:
    number = _number(value, label)
    if number <= 0:
        raise ValueError(f"{label} must be greater than zero.")
    return number


def _positive_int(value: object, label: str) -> int:
    number = _positive_float(value, label)
    if int(number) != number:
        raise ValueError(f"{label} must be an integer.")
    return int(number)


def _non_negative_int(value: object, label: str) -> int:
    number = _number(value, label)
    if number < 0 or int(number) != number:
        raise ValueError(f"{label} must be a non-negative integer.")
    return int(number)
