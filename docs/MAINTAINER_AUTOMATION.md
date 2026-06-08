# Maintainer Automation

## Issue triage

Use labels consistently:

- `bug`: reproducible defect.
- `enhancement`: focused improvement request.
- `docs`: documentation-only change.
- `good-first-issue`: safe scoped contribution.
- `needs-fixture`: report needs a minimal project or sample file.
- `agentic-interface`: output, manifest, or automation contract issue.

Ask for command, expected result, actual result, Python version, Godot version where relevant, and a minimal fixture.

## Release cadence

Use small releases:

- Patch release for bug fixes and docs corrections.
- Minor release for new output formats, rule groups, or config options.
- Keep changelogs per tool because every tool remains standalone.

## Agentic maintenance

Agents should start from:

1. `PROJECT_OVERVIEW.md`
2. `project-metadata.json`
3. The relevant `agent-tool.json`
4. The affected tool README and tests

Prefer JSON output for automated analysis and Markdown or HTML output for human handoff.

## Validation commands

```powershell
python verify_agent_interfaces.py
python -m unittest discover -s tests -v
python -m unittest discover -s godot-project-doctor/tests -v
python -m unittest discover -s godot-ci-doctor-action/tests -v
```

Run each affected package suite from that package directory:

```powershell
python -m unittest discover -s tests -v
```
