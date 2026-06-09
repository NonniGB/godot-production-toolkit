# Project Health

## Scope

Godot Production Toolkit is a collection of narrow production checks for Godot 4 projects. The suite is intended to sit beside a project's normal tests, not replace runtime or gameplay validation.

## Tool Coverage

| Area | Tool |
|---|---|
| Suite orchestration | `godot-project-doctor` |
| GitHub Actions workflow | `godot-ci-doctor-action` |
| Asset import hygiene | `godot-asset-pipeline-doctor` |
| Export preset readiness | `godot-export-preset-doctor` |
| GDScript API comment coverage | `gdscript-api-comment-coverage` |
| Input map coverage | `godot-input-map-auditor` |
| Localization QA | `godot-localization-qa-guard` |
| Save fixture schema checks | `godot-save-schema-guard` |
| Scene signal checks | `godot-scene-signal-auditor` |
| Visual smoke diffing | `godot-visual-smoke-test-kit` |
| Mobile performance diagnostics | `godot-mobile-perf-doctor` |
| Pixel art utility workflows | `pixel-space-asset-toolkit` |

## Maintenance Checks

- `python verify_tool_manifests.py` validates every `tool-manifest.json` manifest.
- `python verify_release_alignment.py` checks release tags, package versions, changelogs, and action examples stay aligned.
- `python project_health_snapshot.py` prints a compact local maintenance snapshot for scheduled checks.
- `python -m unittest discover -s tests -v` validates the root project checks.
- Each Python package has its own unittest suite under `<tool>/tests/`.
- `.github/workflows/ci.yml` runs root checks and package suites.
- `.github/dependabot.yml` keeps selected Python package dependencies visible.

## Known Limitations

- Visual smoke testing requires a project-owned capture command before image comparison.
- Static diagnostics can flag risks, but they cannot prove gameplay behavior.
- Some reports are intentionally conservative and should be tuned with project-specific configuration over time.
- Package publishing can be staged by demand and maintenance capacity.

## Privacy And Fixture Policy

- Public examples should use tiny synthetic Godot fixtures.
- Do not include proprietary projects, private paths, credentials, signing keys, analytics identifiers, or personal contact details in fixtures or reports.
- Prefer redacted issue reproductions with the smallest possible files.
