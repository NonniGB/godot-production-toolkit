# PyPI Release Notes

Package publishing uses PyPI Trusted Publishing rather than local API tokens.

## Published Packages

These packages are published as standalone PyPI distributions:

- [`gdscript-api-comment-coverage`](https://pypi.org/project/gdscript-api-comment-coverage/)
- [`godot-asset-pipeline-doctor`](https://pypi.org/project/godot-asset-pipeline-doctor/)
- [`godot-export-preset-doctor`](https://pypi.org/project/godot-export-preset-doctor/)
- [`godot-input-map-auditor`](https://pypi.org/project/godot-input-map-auditor/)
- [`godot-localization-qa-guard`](https://pypi.org/project/godot-localization-qa-guard/)
- [`godot-mobile-perf-doctor`](https://pypi.org/project/godot-mobile-perf-doctor/)
- [`godot-save-schema-guard`](https://pypi.org/project/godot-save-schema-guard/)
- [`godot-scene-signal-auditor`](https://pypi.org/project/godot-scene-signal-auditor/)
- [`godot-visual-smoke-test-kit`](https://pypi.org/project/godot-visual-smoke-test-kit/)
- [`pixel-space-asset-toolkit`](https://pypi.org/project/pixel-space-asset-toolkit/)

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
| `gdscript-api-comment-coverage` | `publish-gdscript-api-comment-coverage.yml` |
| `godot-asset-pipeline-doctor` | `publish-pypi.yml` |
| `godot-export-preset-doctor` | `publish-export-preset-doctor.yml` |
| `godot-input-map-auditor` | `publish-input-map-auditor.yml` |
| `godot-localization-qa-guard` | `publish-localization-qa-guard.yml` |
| `godot-mobile-perf-doctor` | `publish-mobile-perf-doctor.yml` |
| `godot-save-schema-guard` | `publish-save-schema-guard.yml` |
| `godot-scene-signal-auditor` | `publish-scene-signal-auditor.yml` |
| `godot-visual-smoke-test-kit` | `publish-visual-smoke-test-kit.yml` |
| `pixel-space-asset-toolkit` | `publish-pixel-space-asset-toolkit.yml` |

Each workflow expects PyPI Trusted Publishing with:

- Owner: `NonniGB`
- Repository: `godot-production-toolkit`
- Workflow: the matching workflow filename above
- Environment: `pypi`

PyPI supports pending publishers for new projects, so the first trusted workflow run can create the project after the pending publisher is configured in the PyPI account.
