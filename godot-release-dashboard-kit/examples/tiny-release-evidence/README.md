# Tiny Release Evidence

This folder is a tiny example input for `godot-release-dashboard-kit`.

It includes:

- `export.json`: a small JSON report card with release warnings.
- `mobile-ui.md`: a Markdown note card.
- `mobile-ui-overlay.svg`: a visual artifact preview.
- `scenario-bundle.json`: synthetic scenario evidence with reviewer links.
- `runtime-timeline.json`: a tiny telemetry summary linked from the scenario bundle.
- `run.log` and `junit.xml`: tiny linked files referenced by the scenario bundle.

```powershell
godot-release-dashboard build godot-release-dashboard-kit\examples\tiny-release-evidence --output reports\release-dashboard.html
```
