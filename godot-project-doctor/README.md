# Godot Project Doctor

`godot-project-doctor` is an umbrella CLI for the Godot production toolkit. It plans, runs, and summarizes the standalone tools without hiding their individual commands.

## Install

```powershell
python -m pip install -e .
```

Install the standalone tools you want to run in the same environment.

## Quick Start

Ask the doctor what it sees in a project:

```powershell
godot-project-doctor inspect path\to\godot-project
godot-project-doctor recommend path\to\godot-project
```

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

## Config

Use `examples/godot-project-doctor.toml` as a starting point. Project-audit tools are enabled by default; specialized tools such as save-schema validation, visual smoke plans, and pixel asset commands stay disabled until their required config is supplied.

`recommend` is intentionally conservative. It looks for common project signals
such as `export_presets.cfg`, GDScript files, PNG/import files, localization
files, input-map settings, and data/content folders, then suggests a short check
set with reasons.

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
