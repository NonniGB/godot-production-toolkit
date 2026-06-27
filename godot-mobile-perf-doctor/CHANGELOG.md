# Changelog

## 0.1.8 - 2026-06-27

- Added a stretch aspect warning for phone builds that use `display/window/stretch/aspect="ignore"`.
- Added `--mobile-ui-metadata` and `mobile_ui_metadata` config support so CI can require a project-owned mobile UI or safe-area evidence export.
- Included the configured mobile UI metadata path in JSON, Markdown, text, and SARIF report metadata.

## 0.1.7 - 2026-06-15

- Raised the package build backend floor to `setuptools>=82.0.1`.
- Raised the Pillow dependency floor to `Pillow>=12.2.0`.

## 0.1.6 - 2026-06-09

- Added the active profile description to machine-readable report metadata.

## 0.1.5 - 2026-06-09

- Added built-in mobile budget profiles for portrait, balanced, low-end, and tablet-oriented projects.
- Added `--list-profiles` so teams can see available presets before choosing a config.
- Added report metadata, active budget limits, rule titles, and rule explanations to JSON, text, Markdown, and SARIF reports.

## 0.1.4 - 2026-06-09

- Report invalid TOML configuration as a usage error instead of a traceback.
- Validate config-loaded `format` and `fail_on` values.
- Reject non-positive texture dimension and viewport-pixel limits.

## 0.1.3 - 2026-06-09

- Reported missing `project.godot` files as explicit audit errors.

## 0.1.2 - 2026-06-08

- Added TOML config support for profiles, report output, fail thresholds, texture limits, viewport budgets, and adb summary paths.
- Added configurable viewport pixel budgets for mobile static checks.

## 0.1.1 - 2026-06-08

- Improved the PyPI README with a practical Android test-build workflow and CI example.

## 0.1.0 - 2026-06-08

- Added static `project.godot` settings parser.
- Added renderer, viewport, stretch, and large texture findings.
- Added PNG texture memory summary.
- Added mocked adb summary parser.
- Added text, JSON, and Markdown reports, CLI, tests, CI, docs, and generic fixtures.
