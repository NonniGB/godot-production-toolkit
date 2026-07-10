# Changelog

## 0.1.7 - 2026-07-10

- Improved `migrate-chain` failure reports with the failed step, fixture name,
  expected output path, and captured stdout/stderr snippets.
- Added tests for migration command output capture and chain failure messages.

## 0.1.6 - 2026-06-17

- Added `migrate-chain --compare-original` to compare each original fixture with its final migrated output.
- JSON reports now include migration comparison, migration, validation, and redaction summary counts for dashboards.
- Added rule help and tests for before-and-after migration comparison reports.

## 0.1.5 - 2026-06-17

- Added `generate-fixture` to create deterministic JSON save fixtures from schema defaults, required fields, and explicit overrides.
- Added `migrate-chain --schema` so final migrated fixtures can be validated in the same report after migration commands succeed.
- Added rule help and tests for fixture generation and final migrated-output validation.

## 0.1.4 - 2026-06-17

- Added `redact` to write sanitized copies of selected save fixture paths.
- Added dry-run, wildcard path matching, overwrite protection, rule help, and tests for fixture redaction.

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
