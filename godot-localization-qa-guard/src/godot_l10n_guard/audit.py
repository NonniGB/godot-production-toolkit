from __future__ import annotations

import re
from typing import Iterable

from .models import CsvTable, Finding, PoCatalog, TranslationEntry

Catalog = CsvTable | PoCatalog

BRACE_PLACEHOLDER_RE = re.compile(r"\{[A-Za-z_][A-Za-z0-9_]*\}")
PERCENT_PLACEHOLDER_RE = re.compile(r"(?<!%)%[sdif]")


def audit_catalogs(
    catalogs: list[Catalog],
    *,
    required_languages: set[str],
    source_language: str,
    used_keys: set[str] | None = None,
    max_expansion: float | None = None,
    allowed_glyphs: set[str] | None = None,
) -> list[Finding]:
    findings: list[Finding] = []
    if not catalogs:
        return [Finding("no_catalogs", "error", None, "No translation catalogs were provided.")]

    all_keys: set[str] = set()
    for catalog in catalogs:
        all_keys.update(catalog.keys())
        findings.extend(_catalog_metadata_findings(catalog, required_languages))
        for entry in catalog.entries:
            findings.extend(
                _entry_findings(
                    entry,
                    required_languages,
                    source_language,
                    max_expansion=max_expansion,
                    allowed_glyphs=allowed_glyphs,
                )
            )

    if used_keys is not None:
        for key in sorted(used_keys - all_keys):
            findings.append(Finding("missing_key", "error", key, f"Used key '{key}' is not translated."))
        for key in sorted(all_keys - used_keys):
            findings.append(Finding("unused_key", "warning", key, f"Translated key '{key}' was not seen in scanned project files."))

    return findings


def _catalog_metadata_findings(catalog: Catalog, required_languages: set[str]) -> list[Finding]:
    findings: list[Finding] = []
    if isinstance(catalog, CsvTable):
        if not catalog.has_keys_header:
            findings.append(Finding("csv_missing_keys_header", "error", None, "CSV header must start with keys.", catalog.path))
        if catalog.had_bom:
            findings.append(Finding("utf8_bom_detected", "warning", None, "CSV file starts with a UTF-8 BOM.", catalog.path))
        for key in sorted(catalog.duplicate_keys):
            findings.append(Finding("duplicate_key", "error", key, f"Duplicate translation key '{key}'.", catalog.path))
        missing_languages = sorted(required_languages - set(catalog.languages))
        for language in missing_languages:
            findings.append(Finding("missing_language_column", "error", None, f"CSV is missing required language column '{language}'.", catalog.path))
    else:
        for key in sorted(catalog.duplicate_keys):
            findings.append(Finding("duplicate_key", "error", key, f"Duplicate PO msgid '{key}'.", catalog.path))
    return findings


def _entry_findings(
    entry: TranslationEntry,
    required_languages: set[str],
    source_language: str,
    *,
    max_expansion: float | None = None,
    allowed_glyphs: set[str] | None = None,
) -> list[Finding]:
    findings: list[Finding] = []
    target_languages = required_languages or set(entry.translations)
    if entry.fuzzy:
        findings.append(Finding("fuzzy_translation", "warning", entry.key, "PO entry is marked fuzzy.", entry.path, entry.line))

    for language in sorted(target_languages):
        if language == source_language:
            continue
        value = entry.translations.get(language, "")
        if not value:
            findings.append(Finding("empty_translation", "error", entry.key, f"Missing translation for '{language}'.", entry.path, entry.line))
            continue
        if value == entry.source:
            findings.append(Finding("unchanged_translation", "warning", entry.key, f"Translation for '{language}' matches the source string.", entry.path, entry.line))
        if _placeholders(entry.source) != _placeholders(value):
            findings.append(Finding("placeholder_mismatch", "error", entry.key, f"Placeholder set differs for '{language}'.", entry.path, entry.line))
        if max_expansion and len(entry.source) > 0 and len(value) / len(entry.source) > max_expansion:
            findings.append(
                Finding(
                    "string_expansion",
                    "warning",
                    entry.key,
                    f"Translation for '{language}' is longer than the {max_expansion:.2f} expansion limit.",
                    entry.path,
                    entry.line,
                )
            )
        if allowed_glyphs is not None:
            missing_glyphs = sorted({character for character in value if character not in allowed_glyphs})
            if missing_glyphs:
                preview = "".join(missing_glyphs[:12])
                findings.append(
                    Finding(
                        "glyph_not_allowed",
                        "warning",
                        entry.key,
                        f"Translation for '{language}' uses glyphs outside the configured allow-list: {preview}",
                        entry.path,
                        entry.line,
                    )
                )

    return findings


def _placeholders(text: str) -> set[str]:
    return set(BRACE_PLACEHOLDER_RE.findall(text)) | set(PERCENT_PLACEHOLDER_RE.findall(text))
