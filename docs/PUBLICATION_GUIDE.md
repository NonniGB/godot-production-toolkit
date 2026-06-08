# Publication Guide

## GitHub release

1. Initialize the root repository.
2. Publish it as a public repository named `godot-production-toolkit`.
3. Set the repository About description to: `CI-friendly production diagnostics for Godot 4 projects.`
4. Add topics: `godot`, `godot4`, `gamedev`, `ci`, `github-actions`, `python`, `sarif`, `mobile`, `localization`, `pixel-art`, `testing`, `qa`.
5. Ensure the root README links the project overview, metadata, validation commands, and release checklist.
6. Create a GitHub release for the current version with a concise description of the suite and the main adoption path.
7. Pin action examples to the latest tagged release, currently `@v0.1.2`.

## PyPI release

The highest-demand packages are published on PyPI:

- [`godot-asset-pipeline-doctor`](https://pypi.org/project/godot-asset-pipeline-doctor/)
- [`godot-export-preset-doctor`](https://pypi.org/project/godot-export-preset-doctor/)
- [`godot-mobile-perf-doctor`](https://pypi.org/project/godot-mobile-perf-doctor/)

The `godot-project-doctor` command remains part of the repository, but the exact `godot-project-doctor` distribution name is already used on PyPI. Publish it later under a distinct package name if demand is clear.

Use the manual package-specific GitHub workflow for releases. Each workflow builds one package, runs `twine check`, and publishes through PyPI Trusted Publishing.

For new projects, create pending publishers in PyPI before the first workflow run:

| PyPI project | GitHub owner | Repository | Workflow | Environment |
|---|---|---|---|---|
| `godot-asset-pipeline-doctor` | `NonniGB` | `godot-production-toolkit` | `publish-pypi.yml` | `pypi` |
| `godot-export-preset-doctor` | `NonniGB` | `godot-production-toolkit` | `publish-export-preset-doctor.yml` | `pypi` |
| `godot-mobile-perf-doctor` | `NonniGB` | `godot-production-toolkit` | `publish-mobile-perf-doctor.yml` | `pypi` |

Release package updates one at a time so failures are easy to isolate.

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
