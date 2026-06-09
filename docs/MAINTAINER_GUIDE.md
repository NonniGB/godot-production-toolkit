# Maintainer Guide

## Issue triage

Use labels consistently:

- `bug`: reproducible defect.
- `enhancement`: focused improvement request.
- `docs`: documentation-only change.
- `good-first-issue`: safe scoped contribution.
- `needs-fixture`: report needs a minimal project or sample file.
- `ci`: workflow, report format, manifest, or build issue.

Ask for command, expected result, actual result, Python version, Godot version where relevant, and a minimal fixture.

## Release cadence

Use small releases:

- Patch release for bug fixes and docs corrections.
- Minor release for new output formats, rule groups, or config options.
- Keep changelogs per tool because every tool remains standalone.

## CI and tooling maintenance

For CI, report format, or command-line interface changes, start from:

1. `PROJECT_OVERVIEW.md`
2. `project-metadata.json`
3. The relevant `tool-manifest.json`
4. The affected tool README and tests

Prefer JSON output for scripts and Markdown or HTML output for human review.

## Validation commands

```powershell
python verify_tool_manifests.py
python verify_release_alignment.py
python project_health_snapshot.py
python -m unittest discover -s tests -v
python -m unittest discover -s godot-project-doctor/tests -v
python -m unittest discover -s godot-ci-doctor-action/tests -v
```

Run each affected package suite from that package directory:

```powershell
python -m unittest discover -s tests -v
```
