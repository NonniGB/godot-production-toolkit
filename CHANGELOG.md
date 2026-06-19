# Changelog

## Unreleased

- Improved `godot-scene-signal-auditor` scene contracts with baseline contract
  diff warnings for removed scene API requirements.
- Improved `godot-scene-signal-auditor` scene contracts with node group and
  exported script property checks.
- Improved `godot-gdscript-architecture-guard` with possible unused resource
  summaries for refactor review reports.
- Improved `godot-scenario-report-kit` scenario bundles with compact linked-log
  summaries that avoid embedding log contents.
- Improved `godot-scenario-report-kit` scenario bundles with compact visual
  smoke report summaries for screenshot/capture evidence.
- Improved `godot-runtime-telemetry-lab` adapters for official Godot
  Performance monitor time and memory units.
- Improved `godot-release-dashboard-kit` with export artifact evidence cards
  for exported-folder and exported-file-list reports.
- Improved `godot-release-dashboard-kit` with scenario flake and retry evidence
  sections for `godot-scenario-report-kit` flake comparison reports.
- Improved `godot-scenario-report-kit` flake reports with retry grouping for
  repeated scenario attempts inside a single run folder or result file.
- Improved `godot-gdscript-architecture-guard` with module ownership summaries
  for refactor review reports.
- Improved `godot-save-schema-guard` with before-and-after migration comparison
  summaries for migrated fixtures.
- Improved `godot-release-dashboard-kit` with typed report highlights for
  common toolkit report cards.
- Improved `godot-project-doctor` with focused Android, HTML5/Web,
  localization, runtime evidence, mods/content packs, save migration,
  architecture, visual review, and mobile UI profiles.
- Improved `godot-project-doctor` with package names and compact `pip install`
  guidance in recommendations, profile output, and generated first-run plans.
- Improved `godot-project-doctor` with profile-based Markdown first-run plans
  that include setup notes, commands, config preview, workflow preview, and
  dashboard handoff.
- Improved `godot-release-dashboard-kit` with previous-report comparison cards
  and optional dashboard project/description metadata.
- Improved `godot-release-dashboard-kit` with workflow-grouped report sections
  and optional `workflow`/`category` metadata on source reports.
- Improved `godot-scenario-report-kit` with direct JUnit XML ingestion for
  scenario summaries, comparisons, manifest checks, flake checks, and bundles.
- Improved `godot-gdscript-architecture-guard` with high fan-in/fan-out summaries, possible unused script summaries, and stale module path warnings.
- Improved `godot-save-schema-guard` with schema-based fixture generation and final migrated-output validation for migration chains.
- Improved `godot-release-dashboard-kit` cards with report metadata and
  copyable reproduction commands when reports provide them.
- Improved `godot-pack-mod-doctor` diffs with moved-resource classification,
  content ID conflict checks, and dashboard-friendly risk summaries.
- Added mobile UI overlay support for localized layout-risk JSON reports.
- Added compact telemetry summaries to scenario evidence bundles and release dashboard cards.
- Added dependency and load-order checks for Godot pack/mod manifests.
- Added package foundations for runtime telemetry, pack/mod manifest checks, and static release dashboards.
- Added runtime telemetry timeline reports, starter budget profiles, and a tiny runtime fixture.
- Added scenario manifest coverage, flaky-run comparison, and a public coverage report sample.
- Added export preset matrix and leak-risk reports, including HTML artifacts for release review.
- Added a workflow guide hub, workflow feedback issue template, report schema stability docs/tests, roadmap labels, and a Godot upgrade workflow.
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
