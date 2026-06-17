from __future__ import annotations

from typing import Any


RULES: dict[str, dict[str, str]] = {
    "missing_viewport": {
        "title": "Missing viewport",
        "help": "Add the viewport to metadata.viewports or update the screen viewport name.",
    },
    "duplicate_node_id": {
        "title": "Duplicate node id",
        "help": "Use stable unique ids so reports can track the same control across runs.",
    },
    "node_outside_viewport": {
        "title": "Node outside viewport",
        "help": "Keep UI rectangles inside the exported viewport bounds.",
    },
    "safe_area_overlap": {
        "title": "Safe-area overlap",
        "help": "Move important controls and labels inside the safe-area rectangle.",
    },
    "touch_target_too_small": {
        "title": "Touch target too small",
        "help": "Increase the clickable area or wrap the control in a larger touch zone.",
    },
    "touch_targets_too_close": {
        "title": "Touch targets too close",
        "help": "Add spacing or make only one of the overlapping rectangles interactive.",
    },
    "text_overflow_risk": {
        "title": "Text overflow risk",
        "help": "Allow wrapping, shorten the label, resize the control, or check localized strings.",
    },
    "text_expansion_overflow_risk": {
        "title": "Text expansion overflow risk",
        "help": "Reserve extra width for localized labels or verify expanded strings in this control.",
    },
    "localized_text_overflow_risk": {
        "title": "Localized text overflow risk",
        "help": "Review this control with stress-pack strings, wrapping, or a wider layout.",
    },
    "no_interactive_controls": {
        "title": "No interactive controls",
        "help": "Export buttons, menus, sliders, or touch zones so the screen can be checked.",
    },
}


def enrich_finding(finding: dict[str, Any]) -> dict[str, Any]:
    rule = RULES.get(str(finding.get("rule_id", "")))
    if not rule:
        return finding
    return {
        **finding,
        "rule_title": rule["title"],
        "rule_help": str(finding.get("help") or rule["help"]),
    }


def rule_catalog() -> dict[str, dict[str, str]]:
    return {rule_id: dict(rule) for rule_id, rule in sorted(RULES.items())}
