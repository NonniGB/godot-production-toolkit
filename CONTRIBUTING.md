# Contributing

Focused bug reports, minimal fixtures, docs corrections, and small rule improvements are welcome.

## Local validation

Run root checks from the repository root:

```powershell
python verify_agent_interfaces.py
python -m unittest discover -s tests -v
```

Run affected package tests from that package directory:

```powershell
python -m unittest discover -s tests -v
```

## Pull requests

Keep pull requests narrow. Include the command you ran, the expected result, and the actual result. If a tool output format changes, update the relevant README, `docs/AGENTIC_USAGE.md`, and `agent-tool.json`.

## Release changes

For user-facing behavior, update the relevant `CHANGELOG.md`. For root-level suite behavior, update the root `CHANGELOG.md`, `PROJECT_OVERVIEW.md`, and `project-metadata.json` when the change affects the public project surface.
