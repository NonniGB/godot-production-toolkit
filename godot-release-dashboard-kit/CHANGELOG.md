# Changelog

## 0.1.15 - 2026-07-06

- HTML dashboards now show visual-smoke evidence sections for screenshot
  reports, including capture counts, comparison counts, changed screenshots,
  linked screenshot or diff paths, pixel-change summaries, and findings.
- Scenario bundle cards now surface linked visual-smoke summaries next to
  telemetry and other evidence links.
- Dashboard summaries now include visual-smoke report, capture, comparison, and
  changed-screenshot counts.

## 0.1.14 - 2026-07-05

- HTML dashboards now include a skip link, keyboard focus outlines, accessible
  filter status updates, focusable report cards, and a no-JavaScript note.
- Added print styles so CI dashboard artifacts keep report cards, source links,
  and reproduction commands readable when printed or saved as PDF.

## 0.1.13 - 2026-06-27

- `godot-release-dashboard build` now prints actionable guidance when the input
  folder has no supported report or image files.
- Added `--require-reports` for CI jobs that should fail when a dashboard would
  be empty because the report path is wrong or artifacts were not produced.

## 0.1.12 - 2026-06-27

- Previous-run comparisons now include a compact readiness trend section with
  previous/current blocked, attention, and ready counts.
- Dashboard JSON now exposes `trends.status_counts` and
  `trends.status_deltas` for CI comments or hosted dashboard wrappers.
- HTML dashboards show static readiness bars alongside the existing change
  cards, with no external assets or scripts.

## 0.1.11 - 2026-06-21

- HTML dashboards now include local report filters for blocked, attention,
  ready, and workflow-specific report groups.
- Report cards now carry status and workflow data attributes for static
  filtering without external dependencies.
- Updated package metadata and docs for filtered dashboard output.

## 0.1.10 - 2026-06-17

- Exported-folder and exported-file-list reports now get a dedicated dashboard
  section with file counts, byte totals, SHA-256 coverage, extension counts,
  and a compact file manifest.
- Dashboard summaries now roll up export artifact reports, files, hashed files,
  and private/signing or development-file findings.
- The tiny release evidence fixture now includes a synthetic exported-folder
  inspection report so generated dashboards show export artifact evidence.

## 0.1.9 - 2026-06-17

- Scenario flake comparison reports now get their own dashboard section with
  flaky scenario groups, retry attempts, status sequences, and final statuses.
- Dashboard summaries now roll up scenario flake and retry counts alongside
  scenario bundle and telemetry evidence.
- The tiny release evidence fixture now includes a synthetic scenario retry
  report so generated dashboards demonstrate the new section.

## 0.1.8 - 2026-06-17

- Dashboard cards now show typed highlights for common toolkit report shapes,
  including runtime telemetry, pack/mod, export, asset, content, and save
  reports.
- JSON dashboards now include per-card `highlights` rows for scripts and
  downstream dashboard tooling.

## 0.1.7 - 2026-06-17

- Added `--previous-reports-dir` with `--baseline` as an alias for comparing a
  current reports folder with a previous run.
- HTML dashboards now show trend cards for added, removed, and changed reports,
  including status and error/warning deltas.
- JSON dashboards now include structured `trends` data and optional
  `description` and `project` fields.

## 0.1.6 - 2026-06-17

- Dashboard JSON now includes workflow groups and per-report workflow labels.
- HTML dashboards now render report cards in workflow sections while keeping
  each card's blocked, attention, or ready state visible.
- Reports can provide `workflow` and `category` at the top level, in
  `metadata`, or in `summary`; otherwise the dashboard uses a conservative
  fallback from the tool name, report kind, and path.

## 0.1.5 - 2026-06-17

- Dashboard cards now surface optional report metadata such as tool version,
  schema version, generation time, profile, and risk level.
- JSON reports can now include `command`, `reproduce_command`,
  `reproduction_command`, or `commands` fields that render as copyable
  reproduction commands in the HTML dashboard.
- Dashboard JSON now counts report cards that include reproduction commands.

## 0.1.4 - 2026-06-17

- Scenario bundle cards now show compact runtime telemetry summaries when the bundle includes them.
- Dashboard JSON now rolls up scenario-linked telemetry sample, spike, warning, and error counts.
- The tiny release evidence fixture now includes telemetry summary fields for dashboard examples.

## 0.1.3 - 2026-06-17

- Added scenario bundle awareness for `godot-scenario-report-kit` reports.
- Dashboard JSON now includes scenario bundle, scenario, pass/fail, and evidence counts.
- HTML report cards now show scenario evidence links and listed scenario artifacts.
- Expanded the tiny release evidence fixture with synthetic scenario bundle, log, and JUnit inputs.

## 0.1.2 - 2026-06-16

- Added release readiness grouping for blocked, attention, and ready report cards.
- Added source report links to generated HTML dashboards.
- Included readiness counts in JSON dashboard summaries.

## 0.1.1 - 2026-06-16

- Added PNG, JPG, SVG, and WebP artifact discovery.
- Embedded visual artifacts in the generated self-contained HTML dashboard.
- Included image counts and image metadata in JSON dashboard summaries.

## 0.1.0 - 2026-06-16

- Initial static release dashboard builder.
- Added JSON and Markdown report discovery.
- Added HTML and JSON dashboard output.
