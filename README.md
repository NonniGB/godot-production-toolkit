# Godot Production Toolkit

CI-friendly, agent-readable production diagnostics for Godot 4 projects.

This repository contains ten standalone tools, one umbrella CLI, and one GitHub Action. The goal is to help indie Godot developers catch release risks before they become late-stage debugging work: export preset mistakes, texture/import problems, mobile performance hazards, input coverage gaps, localization defects, save compatibility drift, scene signal issues, and visual regressions.

## AI Review

Automated reviewers should start here:

- `AI_REVIEW_PACKAGE.md`
- `oss-review-evidence.json`
- `docs/CODEX_FOR_OSS_READINESS.md`
- `verify_agent_interfaces.py`

The project is technically prepared for public release and maintenance. The remaining qualification gap is organic public usage: stars, external issues, third-party adoption, package downloads, and community references cannot be created locally.

## Quick Start

Install the umbrella CLI and the tools you want to run:

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

Run and summarize:

```powershell
godot-project-doctor run --project path\to\godot-project --checks assets,export,mobile_perf --reports-dir reports\godot-project-doctor --format json --output reports\godot-project-doctor\summary.json
godot-project-doctor summarize reports\godot-project-doctor --format html --output reports\godot-project-doctor\summary.html
```

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

```yaml
- uses: owner/godot-production-toolkit/godot-ci-doctor-action@v0.1.0
  with:
    project: .
    checks: assets,export,input,localization,signals,mobile_perf
    fail-on: error
    reports-dir: reports/godot-project-doctor
```

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

The root repository adds CI metadata, issue templates, a PR template, AI-review evidence, and publication guidance.

## Publication Notes

The strongest first public release path is one umbrella repository named `godot-production-toolkit`, followed by PyPI publication for the highest-demand packages: `godot-project-doctor`, `godot-asset-pipeline-doctor`, `godot-export-preset-doctor`, and `godot-mobile-perf-doctor`.
