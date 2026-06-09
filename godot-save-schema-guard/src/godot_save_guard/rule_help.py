from __future__ import annotations


RULE_HELP: dict[str, dict[str, str]] = {
    "invalid_json": {
        "title": "Invalid JSON fixture",
        "explanation": "The fixture cannot be parsed, so compatibility checks cannot inspect its saved data.",
    },
    "migration_chain_empty": {
        "title": "Migration chain is empty",
        "explanation": "The chain file did not define any usable migration steps from older saves to newer saves.",
    },
    "migration_chain_planned": {
        "title": "Migration chain planned",
        "explanation": "The command is running in dry-run mode and is reporting the migration steps it would execute.",
    },
    "migration_command_failed": {
        "title": "Migration command failed",
        "explanation": "A project-owned migration command returned a non-zero exit code.",
    },
    "missing_required_property": {
        "title": "Required property missing",
        "explanation": "A save fixture is missing a schema property that the current game version expects.",
    },
    "missing_version_field": {
        "title": "Save version missing",
        "explanation": "Save fixtures should carry a top-level version so migrations and compatibility checks can route them.",
    },
    "no_fixtures": {
        "title": "No save fixtures found",
        "explanation": "No JSON save fixtures were available, so the compatibility check had nothing to validate.",
    },
    "numeric_type_drift": {
        "title": "Numeric type drift",
        "explanation": "A value that should be numeric was saved as text, which can break typed load code or comparisons.",
    },
    "type_mismatch": {
        "title": "Type mismatch",
        "explanation": "A save value has a different JSON type than the schema expects.",
    },
    "unexpected_property": {
        "title": "Unexpected property",
        "explanation": "The fixture contains data outside the schema, which may indicate stale fields or accidental save drift.",
    },
}


def explain_rule(rule_id: str) -> dict[str, str]:
    return RULE_HELP.get(
        rule_id,
        {
            "title": rule_id.replace("_", " ").title(),
            "explanation": "This save-schema rule reported a project-specific issue.",
        },
    )


def catalog_for(rule_ids: set[str]) -> dict[str, dict[str, str]]:
    return {rule_id: explain_rule(rule_id) for rule_id in sorted(rule_ids)}
