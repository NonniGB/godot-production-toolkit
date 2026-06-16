# Project Health

## Scope

Godot Production Toolkit is a collection of narrow production checks for Godot 4 projects. The suite is intended to sit beside a project's normal tests, not replace runtime or gameplay validation.

## Tool Coverage

| Area | Tool |
|---|---|
| Suite orchestration | `godot-project-doctor` |
| GitHub Actions workflow | `godot-ci-doctor-action` |
| Asset import hygiene | `godot-asset-pipeline-doctor` |
| Data content integrity | `godot-content-graph-doctor` |
| Export preset readiness | `godot-export-preset-doctor` |
| GDScript API comment coverage | `gdscript-api-comment-coverage` |
| GDScript architecture checks | `godot-gdscript-architecture-guard` |
| Input map coverage | `godot-input-map-auditor` |
| Localization QA | `godot-localization-qa-guard` |
| Save fixture schema checks | `godot-save-schema-guard` |
| Scenario evidence reports | `godot-scenario-report-kit` |
| Scene signal checks | `godot-scene-signal-auditor` |
| Visual smoke diffing | `godot-visual-smoke-test-kit` |
| Mobile performance diagnostics | `godot-mobile-perf-doctor` |
| Mobile UI readiness | `godot-mobile-ui-doctor` |
| Pack, DLC, and mod manifest checks | `godot-pack-mod-doctor` |
| Release dashboard artifacts | `godot-release-dashboard-kit` |
| Runtime telemetry evidence | `godot-runtime-telemetry-lab` |
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
- The umbrella CLI is source-checkout only until a distinct PyPI distribution name is chosen.

## Privacy And Fixture Policy

- Public examples should use tiny synthetic Godot fixtures.
- Do not include proprietary projects, private paths, credentials, signing keys, analytics identifiers, or personal contact details in fixtures or reports.
- Prefer redacted issue reproductions with the smallest possible files.
