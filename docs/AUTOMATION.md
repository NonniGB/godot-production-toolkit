# Automation and CI Contract

Toolkit commands are designed for non-interactive local scripts and CI jobs.
Install only the packages a workflow uses, write machine-readable reports to a
dedicated reports folder, and retain those files as build artifacts.

## Required checks

From the repository root, maintenance changes should run:

```powershell
python verify_tool_manifests.py
python verify_release_alignment.py
python verify_cli_smoke.py
python -m unittest discover -s tests -v
```

Run each affected package test suite as well. Suite CI repeats the checks on
Python 3.11 and 3.14, builds every distribution, installs all wheels in a clean
environment, and smoke tests the installed console commands.

## Reports

JSON diagnostic reports follow the schemas in [`report-schemas`](report-schemas/README.md).
Malformed or missing reports must be treated as errors. Use `--fail-on none`
only when collecting evidence; apply the intended warning or error threshold in
a later explicit gate.

## Publishing

Each package keeps its registered PyPI trusted-publisher workflow filename.
Every publisher uses the shared resolver to require an exact
`<package>-v<pyproject-version>` tag, then validates the suite, builds and checks
the selected package, and publishes through PyPI trusted publishing.

Publication remains a separate maintainer action after local review and green
Suite CI.
