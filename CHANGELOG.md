# Changelog

## 0.1.2 - 2026-06-08

- Added project-specific configuration for the three published packages:
  asset thresholds, export placeholder handling, and mobile viewport budgets.
- Added tests and documentation for the new configuration options.
- Updated GitHub Action examples to pin the current `v0.1.2` release.
- Added a release-alignment verifier for CI and pre-release checks.
- Added a local maintenance snapshot command and aligned root tool-count metadata.
- Updated release checks to support independent standalone package patch versions.
- Added PyPI publish workflows and release tracking for input map, localization, and save schema tools.

## 0.1.1 - 2026-06-08

- Improved the root README first-run guidance for new Godot users.
- Improved PyPI package READMEs for the three published standalone tools.
- Made issue templates easier to fill in with command, output, fixture, and environment prompts.

## 0.1.0 - 2026-06-08

Initial Godot Production Toolkit release package:

- Ten standalone tools for Godot production diagnostics and pixel asset workflows.
- `godot-project-doctor` umbrella CLI.
- `godot-ci-doctor-action` GitHub Action wrapper.
- JSON, SARIF, Markdown, HTML, Mermaid, and PNG report formats.
- Project overview, metadata, and root maintainer governance files.
- PyPI releases for `godot-asset-pipeline-doctor`, `godot-export-preset-doctor`, and `godot-mobile-perf-doctor`.
