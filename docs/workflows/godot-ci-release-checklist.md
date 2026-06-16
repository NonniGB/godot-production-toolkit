# Godot CI Release Checklist

Use this when a Godot project needs a repeatable CI release check before making
a build available to testers or players. It is a good fit for pull requests,
release branches, and nightly builds where export settings, assets, input maps,
mobile performance settings, and collected reports should be checked together.

Related docs: [Tool Index](../TOOL_INDEX.md) and [Use Cases](../USE_CASES.md).

## Packages

- `godot-project-doctor` for the combined release profile.
- `godot-export-preset-doctor` for export preset checks.
- `godot-mobile-perf-doctor` for mobile-facing renderer and project settings.
- `godot-asset-pipeline-doctor` for texture and import setting checks.
- `godot-release-dashboard-kit` when CI should publish one HTML report.

## Copy-paste commands

```powershell
python -m pip install godot-asset-pipeline-doctor godot-export-preset-doctor godot-input-map-auditor godot-mobile-perf-doctor godot-release-dashboard-kit godot-scenario-report-kit
python -m pip install -e .\godot-project-doctor
godot-project-doctor doctor . --profile release
godot-project-doctor run --project . --checks assets,export,input,mobile_perf --reports-dir reports\godot-project-doctor --format json --output reports\godot-project-doctor\summary.json
godot-scenario-report bundle reports\scenarios --telemetry reports\runtime-timeline.html --visual reports\visual-smoke.json --format json --output reports\scenario-bundle.json
godot-project-doctor summarize reports\godot-project-doctor --format html --output reports\godot-project-doctor\index.html
```

`godot-project-doctor` is installed from a source checkout in this example. If
you only want standalone PyPI packages in CI, run the package-specific commands
from the other workflow pages and combine the reports with
`godot-release-dashboard-kit`.

Use a stricter CI gate after the report format is stable:

```powershell
godot-project-doctor run --project . --checks assets,export,input,mobile_perf --reports-dir reports\godot-project-doctor --format markdown --output reports\godot-project-doctor\summary.md --fail-on warning
```

## Expected inputs

- A Godot project root containing `project.godot`.
- `export_presets.cfg` when export checks are included.
- Imported assets with their `*.import` files.
- Optional `godot-project-doctor.toml` for project-specific paths and checks.

## Expected outputs

- JSON or Markdown release check summaries in `reports\godot-project-doctor`.
- An optional static HTML report at `reports\godot-project-doctor\index.html`.
- A non-zero exit code when findings meet the selected `--fail-on` level.
