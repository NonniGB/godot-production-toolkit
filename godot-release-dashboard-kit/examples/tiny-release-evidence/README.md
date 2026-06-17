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
The JSON examples also include synthetic `workflow` and `category` labels so the
generated dashboard shows grouped release evidence.

```powershell
godot-release-dashboard build godot-release-dashboard-kit\examples\tiny-release-evidence --output reports\release-dashboard.html
```

To show the trend cards, compare this fixture with the previous-run fixture:

```powershell
godot-release-dashboard build godot-release-dashboard-kit\examples\tiny-release-evidence --previous-reports-dir godot-release-dashboard-kit\examples\tiny-release-evidence-previous --title "Godot Toolkit Release Evidence" --description "Synthetic release checks with scenario and runtime evidence" --project "Tiny Godot Fixture" --output reports\release-dashboard.html
```
