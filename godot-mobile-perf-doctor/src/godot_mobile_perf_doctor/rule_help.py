from __future__ import annotations


RULE_HELP: dict[str, dict[str, str]] = {
    "forward_plus_renderer_mobile_risk": {
        "title": "Forward+ renderer selected",
        "explanation": "Forward+ can be expensive for many mobile 2D projects and should be tested carefully on target devices.",
    },
    "large_base_viewport": {
        "title": "Large base viewport",
        "explanation": "A large base viewport can increase fill-rate cost before scaling, especially on phones.",
    },
    "large_texture_dimension": {
        "title": "Large texture dimension",
        "explanation": "Large PNG dimensions can increase memory use, load time, and texture upload cost on mobile devices.",
    },
    "missing_project_godot": {
        "title": "Missing project.godot",
        "explanation": "Project settings could not be audited because the scan root does not contain a Godot project file.",
    },
    "stretch_disabled": {
        "title": "Stretch mode disabled",
        "explanation": "Mobile projects usually need explicit stretch settings so layout and rendering scale predictably.",
    },
}


def explain_rule(rule_id: str) -> dict[str, str]:
    return RULE_HELP.get(
        rule_id,
        {
            "title": rule_id.replace("_", " ").title(),
            "explanation": "This mobile performance rule reported a project-specific issue.",
        },
    )


def catalog_for(rule_ids: set[str]) -> dict[str, dict[str, str]]:
    return {rule_id: explain_rule(rule_id) for rule_id in sorted(rule_ids)}
