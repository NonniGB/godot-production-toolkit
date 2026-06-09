from __future__ import annotations


RULE_HELP: dict[str, dict[str, str]] = {
    "csv_missing_keys_header": {
        "title": "CSV keys header missing",
        "explanation": "Godot CSV translation files should start with a keys column so rows can be matched to translation keys.",
    },
    "duplicate_key": {
        "title": "Duplicate translation key",
        "explanation": "Duplicate keys make it unclear which string should be used at runtime or imported into the editor.",
    },
    "empty_translation": {
        "title": "Empty translation",
        "explanation": "A required target language has no translated text, so players will see missing or fallback copy.",
    },
    "fuzzy_translation": {
        "title": "Fuzzy PO entry",
        "explanation": "Fuzzy gettext entries usually need translator review before shipping.",
    },
    "glyph_not_allowed": {
        "title": "Glyph outside allow-list",
        "explanation": "The translation uses characters that may not be available in the configured UI font.",
    },
    "missing_key": {
        "title": "Used key missing from catalogs",
        "explanation": "Project files reference a translation key that is not present in the loaded catalogs.",
    },
    "missing_language_column": {
        "title": "Required language column missing",
        "explanation": "A required target language was not found in the CSV header.",
    },
    "no_catalogs": {
        "title": "No catalogs provided",
        "explanation": "No CSV or PO translation files were loaded, so localization coverage cannot be checked.",
    },
    "placeholder_mismatch": {
        "title": "Placeholder mismatch",
        "explanation": "Source and translated text use different placeholder sets, which can cause runtime formatting errors.",
    },
    "string_expansion": {
        "title": "String expansion risk",
        "explanation": "The translated text is much longer than the source and may need UI layout review.",
    },
    "unchanged_translation": {
        "title": "Unchanged translation",
        "explanation": "The target text matches the source, which may mean the string has not actually been translated.",
    },
    "unused_key": {
        "title": "Catalog key not seen in project scan",
        "explanation": "The key exists in catalogs but was not found in scanned scripts or scenes.",
    },
    "utf8_bom_detected": {
        "title": "UTF-8 BOM detected",
        "explanation": "A UTF-8 BOM can confuse some text processing tools and should usually be removed from CSV catalogs.",
    },
}


def explain_rule(rule_id: str) -> dict[str, str]:
    return RULE_HELP.get(
        rule_id,
        {
            "title": rule_id.replace("_", " ").title(),
            "explanation": "This localization rule reported a project-specific issue.",
        },
    )


def catalog_for(rule_ids: set[str]) -> dict[str, dict[str, str]]:
    return {rule_id: explain_rule(rule_id) for rule_id in sorted(rule_ids)}
