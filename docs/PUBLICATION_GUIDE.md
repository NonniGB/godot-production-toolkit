# Publication Guide

## GitHub release

1. Initialize the root repository.
2. Publish it as a public repository named `godot-production-toolkit`.
3. Set the repository About description to: `CI-friendly production diagnostics for Godot 4 projects.`
4. Add topics: `godot`, `godot4`, `gamedev`, `ci`, `github-actions`, `python`, `sarif`, `mobile`, `localization`, `pixel-art`, `testing`, `qa`.
5. Ensure the root README links the project overview, metadata, validation commands, and release checklist.
6. Bump the root `pyproject.toml` version to the suite release you are about to tag.
7. Create a GitHub release for the current version with a concise description of the suite and the main adoption path.
8. Pin action examples to the latest tagged release, currently `@v0.1.2`.
9. Run `python verify_release_alignment.py` before tagging to catch stale README, action, changelog, or package-version references.

## PyPI release

The standalone tools are published on PyPI:

- [`gdscript-api-comment-coverage`](https://pypi.org/project/gdscript-api-comment-coverage/)
- [`godot-asset-pipeline-doctor`](https://pypi.org/project/godot-asset-pipeline-doctor/)
- [`godot-content-graph-doctor`](https://pypi.org/project/godot-content-graph-doctor/)
- [`godot-export-preset-doctor`](https://pypi.org/project/godot-export-preset-doctor/)
- [`godot-gdscript-architecture-guard`](https://pypi.org/project/godot-gdscript-architecture-guard/)
- [`godot-input-map-auditor`](https://pypi.org/project/godot-input-map-auditor/)
- [`godot-localization-qa-guard`](https://pypi.org/project/godot-localization-qa-guard/)
- [`godot-mobile-perf-doctor`](https://pypi.org/project/godot-mobile-perf-doctor/)
- [`godot-mobile-ui-doctor`](https://pypi.org/project/godot-mobile-ui-doctor/)
- [`godot-save-schema-guard`](https://pypi.org/project/godot-save-schema-guard/)
- [`godot-scenario-report-kit`](https://pypi.org/project/godot-scenario-report-kit/)
- [`godot-scene-signal-auditor`](https://pypi.org/project/godot-scene-signal-auditor/)
- [`godot-visual-smoke-test-kit`](https://pypi.org/project/godot-visual-smoke-test-kit/)
- [`pixel-space-asset-toolkit`](https://pypi.org/project/pixel-space-asset-toolkit/)

The `godot-project-doctor` command remains part of the repository, but the exact `godot-project-doctor` distribution name is already used on PyPI. Publish it later under a distinct package name if demand is clear.

Use the manual package-specific GitHub workflow for releases. Each workflow builds one package, runs `twine check`, and publishes through PyPI Trusted Publishing.

For new projects, create pending publishers in PyPI before the first workflow run:

| PyPI project | GitHub owner | Repository | Workflow | Environment |
|---|---|---|---|---|
| `gdscript-api-comment-coverage` | `NonniGB` | `godot-production-toolkit` | `publish-gdscript-api-comment-coverage.yml` | `pypi` |
| `godot-asset-pipeline-doctor` | `NonniGB` | `godot-production-toolkit` | `publish-pypi.yml` | `pypi` |
| `godot-content-graph-doctor` | `NonniGB` | `godot-production-toolkit` | `publish-content-graph-doctor.yml` | `pypi` |
| `godot-export-preset-doctor` | `NonniGB` | `godot-production-toolkit` | `publish-export-preset-doctor.yml` | `pypi` |
| `godot-gdscript-architecture-guard` | `NonniGB` | `godot-production-toolkit` | `publish-gdscript-architecture-guard.yml` | `pypi` |
| `godot-mobile-perf-doctor` | `NonniGB` | `godot-production-toolkit` | `publish-mobile-perf-doctor.yml` | `pypi` |
| `godot-mobile-ui-doctor` | `NonniGB` | `godot-production-toolkit` | `publish-mobile-ui-doctor.yml` | `pypi` |
| `godot-input-map-auditor` | `NonniGB` | `godot-production-toolkit` | `publish-input-map-auditor.yml` | `pypi` |
| `godot-localization-qa-guard` | `NonniGB` | `godot-production-toolkit` | `publish-localization-qa-guard.yml` | `pypi` |
| `godot-save-schema-guard` | `NonniGB` | `godot-production-toolkit` | `publish-save-schema-guard.yml` | `pypi` |
| `godot-scenario-report-kit` | `NonniGB` | `godot-production-toolkit` | `publish-scenario-report-kit.yml` | `pypi` |
| `godot-scene-signal-auditor` | `NonniGB` | `godot-production-toolkit` | `publish-scene-signal-auditor.yml` | `pypi` |
| `godot-visual-smoke-test-kit` | `NonniGB` | `godot-production-toolkit` | `publish-visual-smoke-test-kit.yml` | `pypi` |
| `pixel-space-asset-toolkit` | `NonniGB` | `godot-production-toolkit` | `publish-pixel-space-asset-toolkit.yml` | `pypi` |

Release package updates one at a time so failures are easy to isolate. Package patch versions can move independently from the root suite version when only one standalone tool changes.

## Godot community outreach

Start with focused examples rather than broad claims:

- "CI check for Godot export presets before an Android release."
- "Find mobile-unfriendly textures and import settings."
- "Generate a PR artifact summarizing Godot production risks."
- "Use JSON/SARIF output so CI jobs and local scripts can act on findings."

Good places to share after release:

- Godot forum tooling category.
- Godot subreddit.
- Relevant Discord communities.
- Indie developer devlogs where CI tooling is welcome.

## Feedback loop

- Track recurring support questions and turn them into docs.
- Keep release notes tied to user-facing fixes.
- Add minimal fixtures for reproduced defects.
- Prefer small, reviewable changes with validation commands in each pull request.
