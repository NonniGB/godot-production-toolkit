from __future__ import annotations


RULE_HELP: dict[str, dict[str, str]] = {
    "autoload_signal_usage": {
        "title": "Autoload signal connection",
        "explanation": "A script connects to a configured autoload signal, which is useful to review when tracking global coupling.",
    },
    "stale_scene_connection": {
        "title": "Stale scene connection",
        "explanation": "A saved scene connection points at a method that was not found on the resolved target script.",
    },
}


def explain_rule(rule_id: str) -> dict[str, str]:
    return RULE_HELP.get(
        rule_id,
        {
            "title": rule_id.replace("_", " ").title(),
            "explanation": "This signal-auditor rule reported a project-specific issue.",
        },
    )


def catalog_for(rule_ids: set[str]) -> dict[str, dict[str, str]]:
    return {rule_id: explain_rule(rule_id) for rule_id in sorted(rule_ids)}
