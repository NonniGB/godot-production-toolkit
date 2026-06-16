# Project Overview

Godot Production Toolkit is a suite of CI-friendly production diagnostics for Godot 4 projects.

The tools focus on repeated production risks that are easy to miss late in development: export preset mistakes, texture and import hygiene, mobile performance hazards, mobile UI layout risks, input coverage gaps, localization defects, save compatibility drift, scene signal issues, visual regressions, data-content reference errors, scenario and telemetry evidence drift, GDScript architecture coupling, pack/mod manifest checks, release dashboards, and pixel asset workflow checks.

## What Ships

- Seventeen standalone Python CLI packages.
- One umbrella CLI: `godot-project-doctor`.
- One composite GitHub Action: `godot-ci-doctor-action`.
- JSON output for scripts and CI.
- SARIF output for selected CI/code-scanning checks.
- Markdown, HTML, Mermaid, text, PNG diff, and generated asset outputs for human review.
- Root and per-tool tests, examples, contribution docs, security notes, and changelogs.

## Design Principles

- Keep every tool useful on its own.
- Keep command-line behavior noninteractive by default.
- Prefer deterministic checks over opaque analysis.
- Make reports easy to read in a terminal, a browser, or a CI log.
- Avoid project-specific examples in public documentation.
- Avoid network access unless a host platform, such as GitHub Actions, is installing packages.

## Main Entry Points

```powershell
python verify_tool_manifests.py
python -m unittest discover -s tests -v
python -m pip install -e .\godot-project-doctor
godot-project-doctor plan --project path\to\godot-project --format json
```

For a problem-to-tool map, see `docs/TOOL_INDEX.md`. For workflow examples, see
`docs/USE_CASES.md`. For a runnable synthetic fixture with sample reports and
screenshots, see `examples/release-readiness-demo/README.md`.

## Maintenance Model

The repository keeps a normal public project structure:

- `LICENSE`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `SUPPORT.md`
- `CODE_OF_CONDUCT.md`
- `CHANGELOG.md`
- `.github/ISSUE_TEMPLATE/`
- `.github/pull_request_template.md`
- `.github/dependabot.yml`

## Current Limitations

- The tools are intentionally narrow production checks, not a general Godot framework.
- Some checks need project-owned fixtures or baselines to provide their best signal.
- Visual smoke testing still depends on a project-specific capture command before diffing screenshots.
- The umbrella CLI is source-checkout only until a distinct PyPI distribution name is chosen.
