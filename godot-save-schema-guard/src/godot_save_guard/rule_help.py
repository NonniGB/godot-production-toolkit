from __future__ import annotations


RULE_HELP: dict[str, dict[str, str]] = {
    "invalid_json": {
        "title": "Invalid JSON fixture",
        "explanation": "The fixture cannot be parsed, so compatibility checks cannot inspect its saved data.",
    },
    "fixture_generated": {
        "title": "Fixture generated",
        "explanation": "A deterministic save fixture was written from the schema so validation and migration tests have a baseline sample.",
    },
    "fixture_output_exists": {
        "title": "Fixture output exists",
        "explanation": "The generated fixture would replace an existing file. Use overwrite only after reviewing the target path.",
    },
    "fixture_override_invalid": {
        "title": "Fixture override invalid",
        "explanation": "A fixture override could not be applied because the path or JSON value was not valid.",
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
        "explanation": (
            "A project-owned migration command returned a non-zero exit code. "
            "Chain reports include the failed step, expected output, and captured "
            "command output when available."
        ),
    },
    "migration_compare_summary": {
        "title": "Migration comparison summary",
        "explanation": "The original fixture and final migrated fixture were compared so reviewers can see the shape of the save change.",
    },
    "migration_compare_unavailable": {
        "title": "Migration comparison unavailable",
        "explanation": "The tool could not read both fixtures as JSON, so it could not summarize the before-and-after save shape.",
    },
    "migration_path_missing": {
        "title": "Migration path missing",
        "explanation": "A supported save version needs a complete path of migration steps to the current save format.",
    },
    "migration_output_missing": {
        "title": "Migration output missing",
        "explanation": "The migration command succeeded but did not write the expected migrated fixture for validation.",
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
    "redaction_applied": {
        "title": "Redaction applied",
        "explanation": "A sanitized copy was written for review, tests, or public bug reports without changing the original fixture.",
    },
    "redaction_non_scalar_target": {
        "title": "Redaction target is not scalar",
        "explanation": "The configured redaction path points to an object or array, so the tool left it unchanged to avoid damaging fixture structure.",
    },
    "redaction_output_exists": {
        "title": "Redaction output already exists",
        "explanation": "The sanitized fixture would replace an existing file. Use overwrite only after reviewing the target directory.",
    },
    "redaction_path_missing": {
        "title": "Redaction path not found",
        "explanation": "The configured redaction path did not appear in this fixture, which can indicate stale redaction settings or a different save shape.",
    },
    "redaction_planned": {
        "title": "Redaction planned",
        "explanation": "The command is running in dry-run mode and is reporting the values it would redact without writing sanitized files.",
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
