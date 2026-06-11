# Changelog

## 0.1.4 - 2026-06-11

- Added `readiness` command for combining mobile UI metadata with optional input, export, localization, mobile performance, and visual-smoke JSON reports.
- Added Markdown, JSON, and text output for cross-tool mobile readiness summaries.

## 0.1.3 - 2026-06-11

- Added `overlays` command for PNG safe-area, control-bound, and touch-target previews.
- Added visual-smoke viewport support to overlay generation.
- Documented overlay workflows for local review and CI artifacts.

## 0.1.2 - 2026-06-09

- Added `--visual-smoke-plan` for reusing viewport metadata from `godot-visual-smoke plan --format json`.

## 0.1.1 - 2026-06-09

- Added `matrix` command for screen-by-screen mobile UI readiness reports.
- Added per-screen status columns for safe area, touch targets, spacing, text fit, and viewport bounds.
- Updated documentation with a matrix workflow.

## 0.1.0 - 2026-06-09

- Initial mobile UI metadata checker.
- Added safe-area, touch-target, spacing, off-screen, duplicate-id, and text overflow checks.
- Added text, JSON, and Markdown reports.
