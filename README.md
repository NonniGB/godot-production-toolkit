# Godot Production Toolkit

[![Suite CI](https://github.com/NonniGB/godot-production-toolkit/actions/workflows/ci.yml/badge.svg)](https://github.com/NonniGB/godot-production-toolkit/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![godot-asset-pipeline-doctor on PyPI](https://img.shields.io/pypi/v/godot-asset-pipeline-doctor?label=asset%20doctor)](https://pypi.org/project/godot-asset-pipeline-doctor/)
[![godot-export-preset-doctor on PyPI](https://img.shields.io/pypi/v/godot-export-preset-doctor?label=export%20doctor)](https://pypi.org/project/godot-export-preset-doctor/)
[![godot-mobile-perf-doctor on PyPI](https://img.shields.io/pypi/v/godot-mobile-perf-doctor?label=mobile%20perf)](https://pypi.org/project/godot-mobile-perf-doctor/)

CI-friendly production diagnostics for Godot 4 projects.

Godot Production Toolkit helps solo developers and small teams catch release risks before they become late-stage debugging work: export preset mistakes, texture/import problems, mobile performance hazards, input coverage gaps, localization defects, save compatibility drift, scene signal issues, and visual regressions.

It is built as ten standalone command-line tools, one umbrella CLI, and one GitHub Action. Each tool can run locally or in CI, with JSON/SARIF output for build scripts and Markdown/HTML reports for people.

**Fastest path:** install one of the PyPI packages below if you need a single check today, or use the GitHub Action if you want release-readiness reports on every pull request. Use the source checkout when you want the umbrella `godot-project-doctor` command to run several tools together.

![Godot Project Doctor HTML report](docs/assets/screenshots/project-doctor-html-report.png)

## What This Is For

Use the toolkit when you want repeatable checks around practical Godot release work:

- **Before an Android release:** verify export presets, icons, version fields, debug flags, mobile renderer settings, and texture size risks.
- **Before merging a UI/input change:** check that actions still cover keyboard, touch, mouse, and controller targets.
- **Before localizing a build:** catch missing translations, placeholder mismatches, unchanged strings, and unused keys.
- **Before changing save data:** validate save fixtures against a schema and document migration commands.
- **Before shipping visual changes:** compare screenshots against approved baselines.
- **Before reviewing a PR:** produce JSON, Markdown, HTML, and SARIF reports that make failures easier to reproduce.

## Project Map

Start with these files when evaluating or extending the suite:

- `PROJECT_OVERVIEW.md`
- `docs/USE_CASES.md`
- `examples/release-readiness-demo/README.md`
- `docs/PROJECT_HEALTH.md`
- `docs/MAINTAINER_GUIDE.md`
- `verify_tool_manifests.py`

## Quick Start

Install the umbrella CLI and the tools you want to run from a checkout:

```powershell
python -m pip install -e .\godot-project-doctor
python -m pip install -e .\godot-asset-pipeline-doctor
python -m pip install -e .\godot-export-preset-doctor
python -m pip install -e .\godot-mobile-perf-doctor
```

The three first standalone packages are also available from PyPI:

```powershell
python -m pip install godot-asset-pipeline-doctor
python -m pip install godot-export-preset-doctor
python -m pip install godot-mobile-perf-doctor
```

Pick the package that matches the risk you are trying to reduce:

- `godot-export-preset-doctor`: before an Android, Windows, Linux, or web export job.
- `godot-asset-pipeline-doctor`: before merging new sprites, UI art, icons, or large textures.
- `godot-mobile-perf-doctor`: before testing a Godot 4 project on Android hardware.

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

A separate public demo repository shows the GitHub Action in a clean fixture project:

- [godot-production-toolkit-demo](https://github.com/NonniGB/godot-production-toolkit-demo)

## Tool Set

| Tool | Purpose | Script/CI Outputs |
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
- uses: NonniGB/godot-production-toolkit/godot-ci-doctor-action@v0.1.2
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
python verify_tool_manifests.py
python verify_release_alignment.py
python project_health_snapshot.py
python -m unittest discover -s tests -v
```

Run each package suite from that package directory:

```powershell
python -m unittest discover -s tests -v
```

## What's Included

Every standalone tool has the same basic shape so it is easy to browse, test, and package:

- `README.md`
- `LICENSE`
- `CHANGELOG.md`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `tool-manifest.json`
- `docs/AUTOMATION.md`
- `examples/`
- `tests/`
- `pyproject.toml`

The root folder adds CI metadata, issue templates, a PR template, project metadata, and release guidance.

## Maintainer Notes

These root-level files explain how the project is maintained and how contributors can report issues:

- `LICENSE`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `SUPPORT.md`
- `CODE_OF_CONDUCT.md`
- `CHANGELOG.md`
- `.github/CODEOWNERS`
- `.github/dependabot.yml`
- `docs/RELEASE_CHECKLIST.md`
- `docs/MAINTAINER_GUIDE.md`

## Package Publication

The repository is published as one umbrella toolkit. The `godot-project-doctor` command is available from a source checkout, while the highest-demand standalone packages are published on PyPI:

- [`godot-asset-pipeline-doctor`](https://pypi.org/project/godot-asset-pipeline-doctor/)
- [`godot-export-preset-doctor`](https://pypi.org/project/godot-export-preset-doctor/)
- [`godot-mobile-perf-doctor`](https://pypi.org/project/godot-mobile-perf-doctor/)

The exact `godot-project-doctor` distribution name is already used on PyPI, so the umbrella CLI needs a distinct package name before it can be published there.

See [docs/PYPI_RELEASE.md](docs/PYPI_RELEASE.md) for release commands and Trusted Publishing notes.
