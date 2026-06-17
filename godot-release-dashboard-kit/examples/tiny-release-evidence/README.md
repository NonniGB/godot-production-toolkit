# Tiny Release Evidence

This folder is a tiny example input for `godot-release-dashboard-kit`.

It includes:

- `export.json`: a small JSON report card with release warnings.
- `mobile-ui.md`: a Markdown note card.
- `mobile-ui-overlay.svg`: a visual artifact preview.
- `scenario-bundle.json`: synthetic scenario evidence with reviewer links.
- `runtime-timeline.json`: a tiny telemetry summary linked from the scenario bundle.
- `run.log` and `junit.xml`: tiny linked files referenced by the scenario bundle.

Some JSON reports include optional command and metadata fields so the dashboard
can show the command that produced a report, tool versions, schema versions, and
compact risk summaries when that information is available.

```powershell
godot-release-dashboard build godot-release-dashboard-kit\examples\tiny-release-evidence --output reports\release-dashboard.html
```
