from __future__ import annotations


RULE_HELP: dict[str, dict[str, str]] = {
    "visual_diff_threshold_exceeded": {
        "title": "Visual diff threshold exceeded",
        "explanation": "The current screenshot changed more pixels than the configured threshold allows.",
    },
    "visual_image_size_mismatch": {
        "title": "Screenshot size mismatch",
        "explanation": "The baseline and current screenshots have different dimensions, so pixel comparison cannot be trusted.",
    },
}


def explain_rule(rule_id: str) -> dict[str, str]:
    return RULE_HELP.get(
        rule_id,
        {
            "title": rule_id.replace("_", " ").title(),
            "explanation": "This visual smoke rule reported a project-specific issue.",
        },
    )


def catalog_for(rule_ids: set[str]) -> dict[str, dict[str, str]]:
    return {rule_id: explain_rule(rule_id) for rule_id in sorted(rule_ids)}
