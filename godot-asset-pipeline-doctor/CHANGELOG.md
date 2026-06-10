# Changelog

All notable changes to this project are documented here.

## 0.1.8 - 2026-06-10

- Added `manifest contact-sheet` to render sprite manifest thumbnails with anchor markers.
- Added contact sheet documentation and tests for generated PNG output.

## 0.1.7 - 2026-06-09

- Added an `audio-mobile` profile for WAV, OGG, and MP3 budget checks.
- Added audio file-size, WAV duration, large uncompressed audio, and missing import-metadata warnings.
- Added configurable `large_audio_mb` and `max_audio_duration_seconds` thresholds.

## 0.1.6 - 2026-06-09

- Added report metadata with schema version, tool version, root, profile, and supported output formats.
- Added plain-language rule titles and explanations to JSON issues.
- Updated text and SARIF output to use clearer rule names.

## 0.1.5 - 2026-06-09

- Added `manifest check` for sprite metadata files.
- Validates sprite ids, source PNG paths, declared dimensions, and anchor bounds.
- Added sprite manifest documentation and a tiny example manifest.

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
