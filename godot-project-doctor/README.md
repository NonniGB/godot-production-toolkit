# Godot Project Doctor

`godot-project-doctor` is an umbrella CLI for the Godot production toolkit. It recommends package installs, plans, runs, summarizes, compares, and collects the standalone tools without hiding their individual commands.

## Install

```powershell
python -m pip install -e .
```

Install the standalone tools you want to run in the same environment. `recommend`
and `doctor --write-plan` list the package set for each check/profile, so a new
project can start with one focused install command instead of reading every
package README first.

## Quick Start

Ask the doctor what it sees in a project:

```powershell
godot-project-doctor inspect path\to\godot-project
godot-project-doctor recommend path\to\godot-project
godot-project-doctor doctor path\to\godot-project --profile release
godot-project-doctor doctor path\to\godot-project --profile release --write-plan
```

`inspect` reports the project shape, detected Godot signals, sample files, and
the short check list it would start with. `recommend` adds priority, setup
notes, and a dry-run command for each suggested check. `doctor` groups checks
into practical profiles and shows package installs, expected inputs, output
paths, commands, and setup notes. Add `--write-plan` when you want a Markdown
first-run plan with the selected package set, commands, missing inputs, starter
config preview, workflow preview, and dashboard handoff.

Preview a starter config and workflow without writing files:

```powershell
godot-project-doctor init path\to\godot-project --dry-run --include-workflow
```

Preview a CI plan without writing files:

```powershell
godot-project-doctor run --project path\to\godot-project --checks assets,export,mobile_perf --dry-run --format json
```

Summarize existing reports:

```powershell
godot-project-doctor summarize reports\godot-project-doctor --format html --output reports\index.html
```

Compare two report folders:

```powershell
godot-project-doctor compare reports\baseline reports\current --format markdown --fail-on warning
```

Collect reports into one evidence folder:

```powershell
godot-project-doctor collect godot-project-doctor.toml --evidence-dir reports\godot-project-doctor\evidence
```

## Config

Use `examples/godot-project-doctor.toml` as a starting point. Project-audit tools are enabled by default; specialized tools such as save-schema validation, visual smoke plans, pack manifests, runtime telemetry, and pixel asset commands stay disabled until their required config is supplied.

If a config path is missing, the CLI returns a short usage error with the
resolved path and a starter command. Use this when setting up a new project:

```powershell
godot-project-doctor init path\to\godot-project --dry-run --include-workflow
```

## Profile Checklists

Use `doctor` when you want a first-run checklist instead of a raw command list:

```powershell
godot-project-doctor doctor . --profile release
godot-project-doctor doctor . --profile android
godot-project-doctor doctor . --profile html5
godot-project-doctor doctor . --profile mobile --format json
godot-project-doctor doctor . --profile mobile-ui --write-plan
godot-project-doctor doctor . --profile localization --write-plan
godot-project-doctor doctor . --profile runtime --write-plan
godot-project-doctor doctor . --profile release --write-plan
godot-project-doctor doctor . --profile mobile --write-plan --plan-path docs/mobile-check-plan.md
godot-project-doctor doctor . --profile content --write-workflow
godot-project-doctor doctor . --profile save-migration
godot-project-doctor doctor . --profile mods
godot-project-doctor doctor . --profile architecture
godot-project-doctor doctor . --profile visual
godot-project-doctor doctor . --profile qa
```

Profiles are side-effect-free unless `--write-plan` or `--write-workflow` is
passed. The current profiles are:

- `release`: export, asset, input, localization, and mobile performance checks.
- `android`: Android export settings, static mobile performance, input, assets, and localization checks.
- `html5`: web export settings, asset imports, input, localization, and visual smoke planning.
- `mobile`: Android/export, mobile performance, input, mobile UI, and visual smoke planning.
- `mobile-ui`: touch input, mobile UI metadata, localization, visual smoke planning, and mobile settings.
- `localization`: translation files, mobile layout metadata, visual smoke planning, and input text flows.
- `runtime`: scenario reports, runtime telemetry, static performance checks, visual smoke planning, and signal evidence.
- `content`: content graph, save schema, scenario report, pack manifest, and asset checks.
- `save-migration`: save fixtures, schema validation, migration evidence, scenario reports, and content reference checks.
- `mods`: pack manifests, content graph checks, scenario evidence, asset imports, and save compatibility inputs.
- `architecture`: GDScript module boundaries, scene signals, public API comments, and scenario evidence.
- `visual`: screenshot plans, UI metadata, asset imports, localization stress inputs, and input coverage.
- `qa`: scenario, visual smoke, mobile UI, architecture, and signal checks.

`--write-plan` writes a Markdown checklist for the selected profile. The plan
includes a compact `pip install` command for the profile's standalone packages,
ready checks, setup notes for missing inputs, suggested run/collect commands, a
starter config preview, a GitHub Actions preview, and a `godot-release-dashboard`
command for turning the resulting reports into a static review page.

`recommend` is intentionally conservative. It looks for common project signals
such as `export_presets.cfg`, GDScript files, PNG/import files, localization
files, input-map settings, mobile UI metadata, and data/content folders, then
suggests a short check set with reasons.

`collect` writes:

- `manifest.json`: commands, tool versions, run results, and report index.
- `artifacts.json`: artifact paths listed by reports, such as screenshots or diffs.
- `summary.json`: machine-readable combined summary.
- `summary.md`: Markdown report for release notes and PR comments.
- `summary.html`: static report for local review or CI artifacts.

`compare` reads two folders of JSON reports and shows which checks improved,
regressed, appeared, or disappeared. Use `--fail-on error` or `--fail-on warning`
when a CI job should fail only if the current run gets worse than the baseline.

## Explain A Check

```powershell
godot-project-doctor explain content_graph
```

This prints when a check is useful and why it exists.

## Outputs

- `json` for CI and local scripts.
- `markdown` for PR comments and release notes.
- `html` for static artifacts.
- `text` for local terminal use.

## Exit Codes

- `0`: no findings at the selected threshold, or dry-run/plan succeeded.
- `1`: findings met the selected threshold.
- `2`: CLI usage error.
