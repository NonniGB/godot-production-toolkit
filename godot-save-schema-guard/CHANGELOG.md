# Changelog

## Unreleased

- Added `migrate-chain` for ordered save migration steps defined in TOML.
- Added dry-run reports for migration chains so CI can review planned version paths before executing project-owned scripts.

## 0.1.1 - 2026-06-09

- Reported empty fixture directories as explicit validation errors.

## 0.1.0 - 2026-06-08

- Added minimal JSON Schema-like validator for save fixtures.
- Added missing version, numeric type drift, required property, and unexpected property checks.
- Added fixture directory scanning and migration command templating.
- Added text, JSON, and Markdown reports, CLI, tests, CI, docs, and generic fixtures.
