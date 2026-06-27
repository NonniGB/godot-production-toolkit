# Changelog

## 0.1.5 - 2026-06-27

- JSON reports now include a `metadata.rules` catalog with runtime telemetry
  rule titles and help text.
- Findings and timeline spikes now include `rule_title` when the rule is known.

## 0.1.4 - 2026-06-27

- `compare` now reports memory max regressions alongside frame p95 regressions.
- Compare reports now include `frame_p95_delta_ms` and `memory_delta_mb` summary
  fields for scripts, dashboards, and pull request comments.

## 0.1.3 - 2026-06-17

- `adapt` now converts Godot `Performance.TIME_PROCESS` and
  `Performance.TIME_PHYSICS_PROCESS` monitor values from seconds to
  milliseconds.
- `adapt` now treats common Godot render memory monitors as byte values and
  normalizes them to MiB for summary, compare, and timeline input.
- Added a tiny Godot Performance monitor CSV fixture for adapter examples.

## 0.1.2 - 2026-06-16

- Added `adapt` to normalize common Godot monitor, CSV, and debug-exporter field names into toolkit telemetry samples.

## 0.1.1 - 2026-06-16

- Added `timeline` reports with HTML, SVG, Markdown, text, and JSON output.
- Added named runtime budget profiles and `budget init`.
- Added a tiny runtime telemetry fixture for examples and documentation.

## 0.1.0 - 2026-06-16

- Initial runtime telemetry summary and baseline comparison CLI.
- Added JSON, Markdown, and text output.
- Added frame p95 budget and regression findings.
