# Godot Starter Project Audit

Use this when you have a new or unfamiliar Godot 4 project and want a quick
first pass before setting up a full CI pipeline.

The audit runs a small set of practical checks:

- `godot-production-doctor` to install the `godot-project-doctor` command that coordinates the run and summarizes results.
- `godot-export-preset-doctor` for export preset basics.
- `godot-input-map-auditor` for keyboard, touch, mouse, and controller coverage.
- `godot-asset-pipeline-doctor` for texture/import settings.
- `godot-mobile-perf-doctor` for mobile-facing project settings and asset size risks.
- `godot-release-dashboard-kit` to turn the reports into one browsable HTML file.

## Try The Tiny Example

From a source checkout of this repository:

```powershell
python -m pip install -e godot-production-doctor
python -m pip install -e godot-asset-pipeline-doctor -e godot-export-preset-doctor -e godot-input-map-auditor -e godot-mobile-perf-doctor -e godot-release-dashboard-kit

godot-project-doctor run examples\release-readiness-demo\godot-project-doctor.toml --format markdown --output docs\assets\sample-reports\starter-project-audit.md
godot-release-dashboard build docs\assets\sample-reports --title "Starter Project Audit" --project "Tiny Godot Fixture" --description "First-pass Godot release and project setup checks" --output docs\assets\sample-reports\starter-project-audit-dashboard.html
```

The fixture intentionally has a few problems so the reports show useful output:

- an Android export preset with missing package/version/ABI fields;
- input actions without touch coverage;
- pixel-art import settings that can blur or fringe textures;
- mobile project settings that need explicit renderer, viewport, and stretch decisions.

## Run It On Your Project

Create a small `godot-project-doctor.toml` beside your project:

```toml
[project]
path = "."
reports_dir = "reports/starter-audit"
fail_on = "none"
checks = ["assets", "export", "input", "mobile_perf"]

[tools.assets]
args = ["--profile", "pixel-2d", "--fail-on", "none"]

[tools.export]
args = ["--platform", "Android", "--fail-on", "none"]

[tools.input]
args = ["--require", "keyboard,touch", "--fail-on", "none"]

[tools.mobile_perf]
args = ["--profile", "portrait-2d", "--max-texture-dimension", "2048", "--fail-on", "none"]
```

Then run:

```powershell
godot-project-doctor run godot-project-doctor.toml --format markdown --output reports\starter-audit.md
godot-release-dashboard build reports\starter-audit --title "Starter Audit" --project "My Godot Project" --output reports\starter-audit-dashboard.html
```

Use `--fail-on none` for the first pass so you get a full report before
deciding which warnings should become release blockers.

## Sample Output

The checked-in sample report is here:

- [starter-project-audit.md](../assets/sample-reports/starter-project-audit.md)
- [release-readiness-summary.md](../assets/sample-reports/release-readiness-summary.md)
- [release-dashboard-demo.html](../assets/sample-reports/release-dashboard-demo.html)

Excerpt:

```text
Tools: 4
Errors: 7
Warnings: 8

assets: 0 errors, 3 warnings
godot-export-preset-doctor: 4 errors, 2 warnings
godot-input-map-auditor: 3 errors, 0 warnings
godot-mobile-perf-doctor: 0 errors, 3 warnings
```

## Troubleshooting

**Missing Godot binary**

These checks read project files and generated evidence. They do not need to
launch the editor for the tiny example. If your own workflow includes commands
that run Godot, keep the Godot executable path in your project-owned script or
CI job rather than in the toolkit config.

**Missing export templates**

The starter audit checks export preset configuration, package identity, debug
settings, icons, and target options. It does not need export templates unless
you add an actual export step in your own CI job.

**No generated evidence yet**

Early projects often do not have scenario results, screenshots, telemetry, save
fixtures, or content manifests. Start with export, input, asset, and mobile
settings, then add the other workflow reports as those systems become real.

**Too many warnings**

Keep the first report broad. After the first review, move stable decisions into
your config and raise `fail_on` only for checks that should block a branch.
