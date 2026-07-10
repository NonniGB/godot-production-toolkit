from __future__ import annotations


RULE_HELP: dict[str, dict[str, str]] = {
    "collection_input_missing": {
        "title": "Collection input missing",
        "explanation": "A configured collection file does not exist, so the graph cannot be checked reliably.",
        "suggestion": "Create the file or correct the collection path in the configuration.",
    },
    "collection_input_unreadable": {
        "title": "Collection input unreadable",
        "explanation": "A configured collection could not be decoded or parsed.",
        "suggestion": "Check file permissions, encoding, and JSON, CSV, or TOML syntax.",
    },
    "collection_input_unsupported": {
        "title": "Collection input unsupported",
        "explanation": "A configured collection uses an unsupported format or data shape.",
        "suggestion": "Use a JSON, CSV, or TOML file with a list or supported object collection shape.",
    },
    "duplicate_id": {
        "title": "Duplicate id",
        "explanation": "Two or more records in the same collection use the same id, so references may resolve unpredictably.",
        "suggestion": "Rename or merge the duplicate records so every id in the collection is unique.",
    },
    "missing_id": {
        "title": "Missing id",
        "explanation": "A record does not define the id field configured for its collection.",
        "suggestion": "Add the configured id field or adjust the collection config to point at the correct field.",
    },
    "missing_reference": {
        "title": "Missing referenced content",
        "explanation": "A record points at an id that does not exist in the target collection.",
        "suggestion": "Fix the referenced id, add the missing target record, or update the reference field config.",
    },
    "missing_reference_field": {
        "title": "Missing reference field",
        "explanation": "A required reference field is absent from a record.",
        "suggestion": "Add the field, mark the reference optional, or split records that do not use that relationship.",
    },
    "numeric_outlier": {
        "title": "Numeric outlier",
        "explanation": "A configured numeric field is much larger than the collection median.",
        "suggestion": "Check whether the value is intentional or whether a unit, decimal, or copy/paste mistake slipped in.",
    },
    "unknown_target_collection": {
        "title": "Unknown target collection",
        "explanation": "A reference points at a collection name that is not configured.",
        "suggestion": "Add the target collection config or correct the reference collection name.",
    },
    "unused_content": {
        "title": "Unused content",
        "explanation": "A record is not referenced by configured content and is not listed as a root id.",
        "suggestion": "Reference it from another collection, add it to roots, or remove it if it is no longer used.",
    },
}


def explain_rule(rule_id: str) -> dict[str, str]:
    return RULE_HELP.get(
        rule_id,
        {
            "title": rule_id.replace("_", " ").title(),
            "explanation": "This rule reported a content graph issue.",
            "suggestion": "Review the finding message and the collection configuration.",
        },
    )


def catalog_for(rule_ids: set[str]) -> dict[str, dict[str, str]]:
    return {rule_id: explain_rule(rule_id) for rule_id in sorted(rule_ids)}
