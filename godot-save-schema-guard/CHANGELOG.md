# Changelog

## 0.1.3 - 2026-06-16

- Added `migration-graph` to check that supported save versions can reach the current save format through the configured migration chain.
- Added rule help and tests for missing migration paths.

## 0.1.2 - 2026-06-09

- Added `migrate-chain` for ordered save migration steps defined in TOML.
- Added dry-run reports for migration chains so CI can review planned version paths before executing project-owned scripts.
- Added report metadata and plain-language rule explanations to JSON, Markdown, and text output.

## 0.1.1 - 2026-06-09

- Reported empty fixture directories as explicit validation errors.

## 0.1.0 - 2026-06-08

- Added minimal JSON Schema-like validator for save fixtures.
- Added missing version, numeric type drift, required property, and unexpected property checks.
- Added fixture directory scanning and migration command templating.
- Added text, JSON, and Markdown reports, CLI, tests, CI, docs, and generic fixtures.
