# PyPI Release Notes

Package publishing uses PyPI Trusted Publishing rather than local API tokens.

## Published Packages

These packages are published at `0.1.0`:

- [`godot-asset-pipeline-doctor`](https://pypi.org/project/godot-asset-pipeline-doctor/)
- [`godot-export-preset-doctor`](https://pypi.org/project/godot-export-preset-doctor/)
- [`godot-mobile-perf-doctor`](https://pypi.org/project/godot-mobile-perf-doctor/)

The exact `godot-project-doctor` distribution name is already used on PyPI, so do not configure or publish that package name from this repository. If the umbrella CLI is published later, choose a distinct distribution name and update `godot-project-doctor/pyproject.toml` first.

## Local Verification

Run this before publishing:

```powershell
python -m pip install --upgrade build twine
python -m build godot-asset-pipeline-doctor
python -m twine check godot-asset-pipeline-doctor\dist\*
```

Repeat for each package directory.

## GitHub Workflow

Use the manual package workflow for the package being released:

| Package | Workflow file |
|---|---|
| `godot-asset-pipeline-doctor` | `publish-pypi.yml` |
| `godot-export-preset-doctor` | `publish-export-preset-doctor.yml` |
| `godot-mobile-perf-doctor` | `publish-mobile-perf-doctor.yml` |

Each workflow expects PyPI Trusted Publishing with:

- Owner: `NonniGB`
- Repository: `godot-production-toolkit`
- Workflow: the matching workflow filename above
- Environment: `pypi`

PyPI supports pending publishers for new projects, so the first trusted workflow run can create the project after the pending publisher is configured in the PyPI account.
