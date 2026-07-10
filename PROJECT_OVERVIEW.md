# Project Overview

Godot Production Toolkit is a suite of CI and release evidence tools for Godot 4 maintainers.

The tools focus on evidence that maintainers often need before merging or
shipping: export preset mistakes, generated build artifacts, Android/mobile
readiness, localized UI overflow, input coverage, save fixture and migration
drift, screenshot regressions, scenario evidence, runtime telemetry timelines
and budgets, GDScript architecture coupling, pack/mod manifests, and release
dashboard artifacts.

## What Ships

- Seventeen standalone Python CLI packages.
- One umbrella CLI package: `godot-production-doctor`, which installs the
  same-named primary command and the historical `godot-project-doctor` alias.
- Two composite GitHub Actions: `godot-ci-doctor-action` and
  `godot-release-dashboard-action`.
- JSON output for scripts and CI.
- SARIF output for selected CI/code-scanning checks.
- Suite CI on Python 3.11 and 3.14, including all-package wheel builds and clean
  installed-command smoke tests.
- Markdown, HTML, SVG, Mermaid, text, PNG diff, and generated asset outputs for human review.
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
python -m pip install -e .\godot-production-doctor
godot-project-doctor plan --project path\to\godot-project --format json
```

For a problem-to-tool map, see `docs/TOOL_INDEX.md`. For workflow examples
built around maintainer review evidence, see `docs/USE_CASES.md`. For a
runnable synthetic fixture with sample reports and screenshots, see
`examples/release-readiness-demo/README.md`.

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

- The tools are intentionally narrow release-evidence checks, not a general Godot framework.
- Some checks need project-owned fixtures or baselines to provide their best signal.
- Visual smoke testing still depends on a project-specific capture command before diffing screenshots.
- The umbrella package keeps the `godot-project-doctor` command name for continuity.
