# Changelog

## 0.1.5 - 2026-06-27

- Added `capture-plan` for turning stress-pack manifests into locale, screen, and viewport screenshot matrices.
- Added JSON, Markdown, and text output for capture plans.
- Documented how capture plans fit with mobile UI layout-risk and visual smoke checks.

## 0.1.4 - 2026-06-17

- Added `stress-pack` for deterministic pseudo, long, compact, and RTL-like CSV catalogs.
- Added a stress-pack manifest and text, JSON, and Markdown summary output.
- Documented localization stress packs for mobile UI overflow review and CI artifacts.

## 0.1.3 - 2026-06-09

- Added optional string expansion and glyph allow-list checks.
- Added pseudo-localized CSV output for quick UI stress testing.
- Added report metadata and plain-language rule explanations to JSON, Markdown, text, and SARIF output.

## 0.1.2 - 2026-06-09

- Report missing explicit CSV, PO, and translations-directory paths as usage errors.

## 0.1.1 - 2026-06-09

- Added `--scan-all` to scan scripts and scenes for translation-key usage together.

## 0.1.0 - 2026-06-08

- Added Godot CSV parser with duplicate-key and BOM detection.
- Added gettext PO parser with fuzzy, empty, and duplicate entry support.
- Added placeholder mismatch, unchanged target, missing key, and unused key checks.
- Added script and scene key scanning.
- Added text, JSON, and Markdown reports, CLI, tests, CI, docs, and a generic sample project.
