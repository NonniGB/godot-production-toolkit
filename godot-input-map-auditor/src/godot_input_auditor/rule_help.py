from __future__ import annotations


RULE_HELP: dict[str, dict[str, str]] = {
    "action_has_no_events": {
        "title": "Action has no events",
        "explanation": "The action exists but has no key, mouse, gamepad, or touch binding, so players cannot trigger it.",
    },
    "duplicate_binding": {
        "title": "Duplicate binding",
        "explanation": "The same normalized input binding is assigned to multiple actions, which can make controls ambiguous.",
    },
    "input_map_empty": {
        "title": "Input map is empty",
        "explanation": "No actions were found in the project input map, so input coverage cannot be checked.",
    },
    "missing_required_device": {
        "title": "Required device missing",
        "explanation": "An action is missing one of the configured device families such as keyboard, mouse, gamepad, or touch.",
    },
}


def explain_rule(rule_id: str) -> dict[str, str]:
    return RULE_HELP.get(
        rule_id,
        {
            "title": rule_id.replace("_", " ").title(),
            "explanation": "This input-map rule reported a project-specific issue.",
        },
    )


def catalog_for(rule_ids: set[str]) -> dict[str, dict[str, str]]:
    return {rule_id: explain_rule(rule_id) for rule_id in sorted(rule_ids)}
