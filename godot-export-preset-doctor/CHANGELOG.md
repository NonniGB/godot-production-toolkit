# Changelog

## Unreleased

- Added report metadata and plain-language rule explanations to JSON, text, and SARIF output.

## 0.1.5 - 2026-06-09

- Validate `format` and `fail_on` values loaded from TOML config files.

## 0.1.4 - 2026-06-09

- Reported invalid TOML config files as clear CLI usage errors.

## 0.1.3 - 2026-06-09

- Added CLI flags for required Android ABIs and allowed credential placeholder patterns.
- Added tests for no-config CI use of ABI and placeholder overrides.

## 0.1.2 - 2026-06-08

- Added `allowed_secret_patterns` config for deliberate credential placeholders in export presets.
- Added tests for placeholder handling in the CLI and rule engine.

## 0.1.1 - 2026-06-08

- Improved the PyPI README with concrete release-gating and CI examples.

## 0.1.0 - 2026-06-08

- Added Godot `export_presets.cfg` parsing.
- Added Android release-readiness checks for package id, version, ABI, icons, debug options, and credentials.
- Added text, JSON, and SARIF reports.
- Added CLI, tests, CI workflow, docs, and a generic sample project.
