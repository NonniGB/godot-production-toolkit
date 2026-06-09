# Changelog

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
