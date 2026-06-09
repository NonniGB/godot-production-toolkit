# Changelog

All notable changes to this project are documented here.

## 0.1.4 - 2026-06-09

- Report invalid TOML configuration as a usage error instead of a traceback.
- Reject non-positive texture dimension, texture memory, and palette limits.

## 0.1.3 - 2026-06-09

- Created parent directories automatically when writing report output files.

## 0.1.2 - 2026-06-08

### Added

- Added configurable texture-dimension, texture-memory, and palette thresholds through CLI flags and TOML config.
- Added tests for project-specific asset rule thresholds.

## 0.1.1 - 2026-06-08

### Changed

- Improved the PyPI README with a clearer first-use workflow, CI example, and release-review guidance.

## 0.1.0 - 2026-06-08

### Added

- Initial `godot-asset-doctor` CLI.
- PNG inspection for dimensions, alpha use, palette size, estimated RGBA memory, and transparent RGB contamination.
- Godot `.import` parser for common `params` values.
- `pixel-2d`, `android-mobile`, and `default` rule profiles.
- Text and JSON reports.
- Config file support through `.godot-asset-doctor.toml`.
- Default artifact-folder ignores and project-relative exclude globs.
- Unit and fixture tests using Python's standard `unittest`.
