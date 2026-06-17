# Changelog

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
