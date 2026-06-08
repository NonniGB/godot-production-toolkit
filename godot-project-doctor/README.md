# Godot Project Doctor

`godot-project-doctor` is an umbrella CLI for the Godot production toolkit. It plans, runs, and summarizes the standalone tools without hiding their individual commands.

## Install

```powershell
python -m pip install -e C:\Temp\tools\godot-project-doctor
```

Install the standalone tools you want to run in the same environment.

## Quick Start

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

## Outputs

- `json` for agents and CI.
- `markdown` for PR comments and release notes.
- `html` for static artifacts.
- `text` for local terminal use.

## Exit Codes

- `0`: no findings at the selected threshold, or dry-run/plan succeeded.
- `1`: findings met the selected threshold.
- `2`: CLI usage error.
