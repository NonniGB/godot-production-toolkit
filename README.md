# Godot Production Toolkit

[![Suite CI](https://github.com/NonniGB/godot-production-toolkit/actions/workflows/ci.yml/badge.svg)](https://github.com/NonniGB/godot-production-toolkit/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

CI-friendly production diagnostics for Godot 4 projects.

Godot Production Toolkit helps solo developers and small teams catch release risks before they become late-stage debugging work: export preset mistakes, texture/import problems, mobile performance hazards, input coverage gaps, localization defects, save compatibility drift, scene signal issues, and visual regressions.

It is built as ten standalone command-line tools, one umbrella CLI, and one GitHub Action. Each tool can run locally, in CI, or from an agent workflow using structured JSON/SARIF output.

![Godot Project Doctor HTML report](docs/assets/screenshots/project-doctor-html-report.png)

## What This Is For

Use the toolkit when you want repeatable checks around practical Godot release work:

- **Before an Android release:** verify export presets, icons, version fields, debug flags, mobile renderer settings, and texture size risks.
- **Before merging a UI/input change:** check that actions still cover keyboard, touch, mouse, and controller targets.
- **Before localizing a build:** catch missing translations, placeholder mismatches, unchanged strings, and unused keys.
- **Before changing save data:** validate save fixtures against a schema and document migration commands.
- **Before shipping visual changes:** compare screenshots against approved baselines.
- **Before reviewing a PR with an agent:** produce JSON, Markdown, HTML, and SARIF reports that are easy to parse.

## Project Map

Start with these files when evaluating or extending the suite:

- `PROJECT_OVERVIEW.md`
- `docs/USE_CASES.md`
- `examples/release-readiness-demo/README.md`
- `project-metadata.json`
- `docs/PROJECT_HEALTH.md`
- `docs/MAINTAINER_AUTOMATION.md`
- `verify_agent_interfaces.py`

## Quick Start

Install the umbrella CLI and the tools you want to run from a checkout:

```powershell
python -m pip install -e .\godot-project-doctor
python -m pip install -e .\godot-asset-pipeline-doctor
python -m pip install -e .\godot-export-preset-doctor
python -m pip install -e .\godot-mobile-perf-doctor
```

Preview checks without writing files:

```powershell
godot-project-doctor run --project path\to\godot-project --checks assets,export,mobile_perf --dry-run --format json
```

Run checks and summarize the generated reports:

```powershell
godot-project-doctor run --project path\to\godot-project --checks assets,export,mobile_perf --reports-dir reports\godot-project-doctor --format json --output reports\godot-project-doctor\summary.json
godot-project-doctor summarize reports\godot-project-doctor --format html --output reports\godot-project-doctor\summary.html
```

## Try The Included Demo

The repository includes a tiny synthetic Godot fixture with intentionally broken release settings:

```powershell
godot-project-doctor run examples\release-readiness-demo\godot-project-doctor.toml --format markdown --output docs\assets\sample-reports\release-readiness-summary.md
godot-project-doctor summarize docs\assets\sample-reports --format html --output docs\assets\sample-reports\release-readiness-summary.html
```

![Godot Project Doctor terminal demo](docs/assets/screenshots/project-doctor-terminal.png)

The demo shows how the toolkit reports incomplete Android export settings, risky pixel-art import settings, missing input-device coverage, and mobile performance warnings.

## Tool Set

| Tool | Purpose | Agent/CI Outputs |
|---|---|---|
| `godot-project-doctor` | Umbrella CLI for planning, running, and summarizing the suite. | JSON, Markdown, HTML |
| `godot-ci-doctor-action` | GitHub composite action wrapper. | JSON, Markdown, HTML artifacts |
| `godot-asset-pipeline-doctor` | PNG and `.import` checks for pixel art and mobile memory risks. | JSON, SARIF |
| `godot-export-preset-doctor` | Release-readiness checks for `export_presets.cfg`. | JSON, SARIF |
| `gdscript-api-comment-coverage` | Public GDScript API docs and comment coverage gate. | JSON, Markdown |
| `godot-input-map-auditor` | Input device coverage and duplicate binding checks. | JSON, SARIF, Markdown |
| `godot-localization-qa-guard` | CSV/PO localization QA and translation-key usage scan. | JSON, SARIF, Markdown |
| `godot-save-schema-guard` | Save fixture schema validation and migration command checks. | JSON, Markdown |
| `godot-scene-signal-auditor` | Scene signal connection and autoload coupling analysis. | JSON, Mermaid |
| `godot-visual-smoke-test-kit` | Screenshot diffing, approval, and Godot capture command planning. | JSON, PNG diffs |
| `godot-mobile-perf-doctor` | Static mobile performance diagnostics. | JSON, SARIF, Markdown |
| `pixel-space-asset-toolkit` | Deterministic pixel sci-fi asset utilities and galleries. | JSON, PNG, HTML |

## GitHub Action

Add the suite to a Godot project with one workflow step:

```yaml
- uses: NonniGB/godot-production-toolkit/godot-ci-doctor-action@v0.1.0
  with:
    project: .
    checks: assets,export,input,localization,signals,mobile_perf
    fail-on: error
    reports-dir: reports/godot-project-doctor
```

Upload `reports/godot-project-doctor` as a workflow artifact to keep JSON, Markdown, and HTML reports with each run.

## Validation

Run from the repository root:

```powershell
python verify_agent_interfaces.py
python -m unittest discover -s tests -v
```

Run each package suite from that package directory:

```powershell
python -m unittest discover -s tests -v
```

## Repository Contract

Every standalone tool includes:

- `README.md`
- `LICENSE`
- `CHANGELOG.md`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `agent-tool.json`
- `docs/AGENTIC_USAGE.md`
- `examples/`
- `tests/`
- `pyproject.toml`

The root repository adds CI metadata, issue templates, a PR template, project metadata, and release guidance.

## Maintainer Surface

Root-level governance files are included so contributors do not need to inspect every package before understanding the maintenance model:

- `LICENSE`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `SUPPORT.md`
- `CODE_OF_CONDUCT.md`
- `CHANGELOG.md`
- `.github/CODEOWNERS`
- `.github/dependabot.yml`
- `docs/RELEASE_CHECKLIST.md`
- `docs/MAINTAINER_AUTOMATION.md`

## Package Publication

The repository is published as one umbrella toolkit. Package publication can be staged for the highest-demand tools: `godot-project-doctor`, `godot-asset-pipeline-doctor`, `godot-export-preset-doctor`, and `godot-mobile-perf-doctor`.
