# Contributing Fixtures And Sample Reports

Small fixtures are useful when they make a command, report shape, or workflow
easier to reproduce. Keep them synthetic, minimal, and safe to publish.

## Good Fixture Candidates

- A tiny `project.godot` plus the one file a tool needs, such as
  `export_presets.cfg`, `mobile-ui.json`, `content-graph.toml`, or a scenario
  result JSON.
- A reduced report that demonstrates one schema field, warning, or dashboard
  card.
- A short README command that regenerates the report from the fixture.
- A screenshot or terminal capture only when it clarifies the report.

## Do Not Include

- Private game assets, paid assets, unreleased project names, or proprietary
  source files.
- Signing keys, store credentials, deploy tokens, personal access tokens, API
  keys, private URLs, or private local paths.
- Full project dumps. Reduce the fixture to the smallest files needed for the
  command under review.
- Player data, save files, logs, telemetry, or screenshots that contain personal
  information.

## Where Fixtures Belong

- Tool-specific inputs belong under `<tool>/examples/` when they demonstrate one
  package.
- Cross-tool workflows belong under `examples/demo-paths/` when they connect
  several packages.
- Generated snapshots belong under `docs/assets/sample-reports/` when they are
  stable enough to show in docs.
- Screenshots and terminal captures belong under `docs/assets/screenshots/`.

## Pull Request Checklist

- Include the exact command used to regenerate the report.
- Keep generated reports compact enough to review in a browser or terminal.
- Run `python -m unittest discover -s tests -v` from the repository root.
- Run the affected package tests when a fixture exercises package behavior.
- If a JSON report shape changes, update the relevant report schema or explain
  why the existing schema still applies.

