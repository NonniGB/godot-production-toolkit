# PyPI Release Notes

Package publishing uses PyPI Trusted Publishing rather than local API tokens.

## Published Packages

These packages are published as standalone PyPI distributions:

| Package | Current Version |
|---|---:|
| [`gdscript-api-comment-coverage`](https://pypi.org/project/gdscript-api-comment-coverage/) | `0.1.2` |
| [`godot-asset-pipeline-doctor`](https://pypi.org/project/godot-asset-pipeline-doctor/) | `0.1.5` |
| [`godot-content-graph-doctor`](https://pypi.org/project/godot-content-graph-doctor/) | `0.1.1` |
| [`godot-export-preset-doctor`](https://pypi.org/project/godot-export-preset-doctor/) | `0.1.5` |
| [`godot-gdscript-architecture-guard`](https://pypi.org/project/godot-gdscript-architecture-guard/) | `0.1.0` |
| [`godot-input-map-auditor`](https://pypi.org/project/godot-input-map-auditor/) | `0.1.2` |
| [`godot-localization-qa-guard`](https://pypi.org/project/godot-localization-qa-guard/) | `0.1.2` |
| [`godot-mobile-perf-doctor`](https://pypi.org/project/godot-mobile-perf-doctor/) | `0.1.4` |
| [`godot-mobile-ui-doctor`](https://pypi.org/project/godot-mobile-ui-doctor/) | `0.1.1` |
| [`godot-save-schema-guard`](https://pypi.org/project/godot-save-schema-guard/) | `0.1.1` |
| [`godot-scenario-report-kit`](https://pypi.org/project/godot-scenario-report-kit/) | `0.1.0` |
| [`godot-scene-signal-auditor`](https://pypi.org/project/godot-scene-signal-auditor/) | `0.1.1` |
| [`godot-visual-smoke-test-kit`](https://pypi.org/project/godot-visual-smoke-test-kit/) | `0.1.1` |
| [`pixel-space-asset-toolkit`](https://pypi.org/project/pixel-space-asset-toolkit/) | `0.1.1` |

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
| `godot-content-graph-doctor` | `publish-content-graph-doctor.yml` |
| `godot-export-preset-doctor` | `publish-export-preset-doctor.yml` |
| `godot-gdscript-architecture-guard` | `publish-gdscript-architecture-guard.yml` |
| `godot-input-map-auditor` | `publish-input-map-auditor.yml` |
| `godot-localization-qa-guard` | `publish-localization-qa-guard.yml` |
| `godot-mobile-perf-doctor` | `publish-mobile-perf-doctor.yml` |
| `godot-mobile-ui-doctor` | `publish-mobile-ui-doctor.yml` |
| `godot-save-schema-guard` | `publish-save-schema-guard.yml` |
| `godot-scenario-report-kit` | `publish-scenario-report-kit.yml` |
| `godot-scene-signal-auditor` | `publish-scene-signal-auditor.yml` |
| `godot-visual-smoke-test-kit` | `publish-visual-smoke-test-kit.yml` |
| `pixel-space-asset-toolkit` | `publish-pixel-space-asset-toolkit.yml` |

Each workflow expects PyPI Trusted Publishing with:

- Owner: `NonniGB`
- Repository: `godot-production-toolkit`
- Workflow: the matching workflow filename above
- Environment: `pypi`

PyPI supports pending publishers for new projects, so the first trusted workflow run can create the project after the pending publisher is configured in the PyPI account.

The first-release package workflows for `godot-content-graph-doctor`,
`godot-scenario-report-kit`, `godot-gdscript-architecture-guard`, and
`godot-mobile-ui-doctor` also accept package-specific tags:

```powershell
git tag godot-content-graph-doctor-v0.1.1
git tag godot-scenario-report-kit-v0.1.0
git tag godot-gdscript-architecture-guard-v0.1.0
git tag godot-mobile-ui-doctor-v0.1.0
git push origin godot-content-graph-doctor-v0.1.0 godot-scenario-report-kit-v0.1.0 godot-gdscript-architecture-guard-v0.1.0 godot-mobile-ui-doctor-v0.1.0
```
