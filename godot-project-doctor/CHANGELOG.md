# Changelog

## 0.8.4 - 2026-06-27

- Missing `godot-project-doctor.toml` paths now return a concise usage error
  with starter-config guidance instead of a Python traceback.

## 0.1.8 - 2026-06-17

- Added focused doctor profiles for Android, HTML5/Web, localization, runtime
  evidence, mods/content packs, save migration, architecture, visual review,
  and mobile UI work.
- Added pack/mod manifest and runtime telemetry checks to profile planning.

## 0.1.7 - 2026-06-17

- Added package names and `pip install` guidance to `recommend`, `doctor`, and
  generated first-run plans.
- Guided plans now include a compact install section and per-check package
  table before the run commands.

## 0.1.6 - 2026-06-17

- Added `doctor --write-plan` for writing a Markdown first-run plan from a
  selected profile.
- Guided plans include ready checks, missing-input setup notes, suggested
  run/collect/dashboard commands, a starter config preview, and a GitHub Actions
  preview.

## 0.1.5 - 2026-06-16

- Added `doctor --profile release|mobile|content|qa` for profile-based first-run guidance.
- Added task lists with expected inputs, output paths, commands, setup notes, and JSON output.
- Added optional `--write-workflow` support for writing a starter GitHub Actions workflow only when requested.

## 0.1.4 - 2026-06-09

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
