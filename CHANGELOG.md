# Changelog

## Unreleased

- Added package foundations for runtime telemetry, pack/mod manifest checks, and static release dashboards.
- Added runtime telemetry timeline reports, starter budget profiles, and a tiny runtime fixture.
- Added scenario manifest coverage, flaky-run comparison, and a public coverage report sample.
- Added `godot-content-graph-doctor` for data-driven content id, reference, unused-content, numeric outlier, and Mermaid graph checks.
- Added `godot-scenario-report-kit` for scenario evidence summaries and baseline comparisons.
- Added `godot-gdscript-architecture-guard` for module boundary, autoload access, dependency graph, and SARIF checks.
- Added `inspect`, `recommend`, `init`, and `explain` commands to `godot-project-doctor`.
- Expanded README guidance with a choose-by-problem table, new package examples, and report screenshots.
- Added a visible package-version table to the README.
- Improved CLI ergonomics across the standalone packages.
- Tightened validation and error handling across six standalone package CLIs.

## 0.1.2 - 2026-06-08

- Added project-specific configuration for the three published packages:
  asset thresholds, export placeholder handling, and mobile viewport budgets.
- Added tests and documentation for the new configuration options.
- Updated GitHub Action examples to pin the current `v0.1.2` release.
- Added a release-alignment verifier for CI and pre-release checks.
- Added a local maintenance snapshot command and aligned root tool-count metadata.
- Updated release checks to support independent standalone package patch versions.
- Added PyPI publish workflows and release tracking for input map, localization, and save schema tools.
- Added PyPI publish workflows and release tracking for scene signal and visual smoke tools.
- Added PyPI publish workflows and release tracking for API coverage and pixel asset tools.

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
