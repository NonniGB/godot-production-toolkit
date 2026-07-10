# Godot CI Doctor Action

This composite action installs the Godot CI and release evidence tools, runs
`godot-production-doctor`, and writes JSON, Markdown, and HTML summaries for
GitHub Actions artifacts.

## Usage

```yaml
name: Godot release evidence

on:
  pull_request:
  push:
    branches: [main]

jobs:
  doctor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0
      - uses: NonniGB/godot-production-toolkit/godot-ci-doctor-action@06d66f390a45743b4437d09bc63eb8778b52c0a4
        with:
          project: .
          checks: assets,export,input,localization,signals,mobile_perf
          tool-packages: godot-production-doctor godot-asset-pipeline-doctor godot-export-preset-doctor godot-input-map-auditor godot-localization-qa-guard godot-scene-signal-auditor godot-mobile-perf-doctor
          fail-on: error
          reports-dir: reports/godot-project-doctor
      - uses: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02
        if: always()
        with:
          name: godot-doctor-reports
          path: reports/godot-project-doctor
```

## Local Reproduction

Run the same checks locally before pushing:

```powershell
godot-production-doctor run --project . --checks assets,export,input,localization,signals,mobile_perf --reports-dir reports/godot-project-doctor --format json --output reports/godot-project-doctor/summary.json
godot-production-doctor summarize reports/godot-project-doctor --format html --output reports/godot-project-doctor/summary.html
```

## Artifacts

The action writes:

- `summary.json` for CI processing and local scripts.
- `summary.md` for PR comments and release notes.
- `summary.html` for a static human-readable report.
- SARIF files when enabled by individual tools or future `godot-project-doctor` config.

## Inputs

- `project`: Godot project path.
- `config`: optional `godot-project-doctor.toml`.
- `checks`: comma-separated check ids.
- `reports-dir`: artifact directory.
- `fail-on`: `none`, `warning`, or `error`.
- `output-formats`: `json`, `markdown`, `html`.
- `tool-packages`: shell-style package list to install before running.
