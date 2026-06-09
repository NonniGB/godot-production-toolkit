# Changelog

## Unreleased

- Added `compare` for checking report folders against an earlier run.
- Added JSON, Markdown, and text comparison output with optional regression-based exit codes.

## 0.1.3 - 2026-06-09

- Expanded `inspect` with project shape counts, sample paths, project name detection, and test framework hints.
- Updated `recommend` output with priority labels, setup notes, and ready-to-try command hints.
- Improved recommendations for projects with GUT/GdUnit4 or scenario-style test evidence.

## 0.1.2 - 2026-06-09

- Added `collect` to write a compact evidence folder with manifest and summary reports.
- Added `mobile_ui` check planning for `godot-mobile-ui-doctor` metadata reports.
- Updated project inspection and recommendations to detect mobile UI metadata files.

## 0.1.1 - 2026-06-09

- Added `inspect` and `recommend` commands for project-aware check selection.
- Added `init --dry-run` to preview a starter config and optional GitHub Actions workflow.
- Added `explain` for concise check guidance.
- Added content graph support to umbrella check planning.

## 0.1.0 - 2026-06-08

- Initial umbrella CLI with plan, run, dry-run, and summarize commands.
- Added JSON, Markdown, text, and static HTML report output.
