# PyPI Release Notes

The first package release should use PyPI Trusted Publishing rather than a local API token.

## Release Order

1. `godot-project-doctor`
2. `godot-asset-pipeline-doctor`
3. `godot-export-preset-doctor`
4. `godot-mobile-perf-doctor`

## Local Verification

Run this before publishing:

```powershell
python -m pip install --upgrade build twine
python -m build godot-project-doctor
python -m twine check godot-project-doctor\dist\*
```

Repeat for each package directory.

## GitHub Workflow

Use the manual `Publish Python Packages` workflow and select one package at a time.

The workflow expects PyPI Trusted Publishing with:

- Owner: `NonniGB`
- Repository: `godot-production-toolkit`
- Workflow: `publish-pypi.yml`
- Environment: `pypi`

PyPI supports pending publishers for new projects, so the first trusted workflow run can create the project after the pending publisher is configured in the PyPI account.
