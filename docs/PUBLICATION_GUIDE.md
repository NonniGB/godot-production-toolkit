# Publication Guide

## GitHub release

1. Initialize the root repository.
2. Publish it as a public repository named `godot-production-toolkit`.
3. Ensure the root README links `AI_REVIEW_PACKAGE.md`, `oss-review-evidence.json`, and `docs/CODEX_FOR_OSS_READINESS.md`.
4. Create a `v0.1.0` release with a concise description of the suite and the first adoption path.
5. Pin the action example to `@v0.1.0`.

## PyPI release

Publish the highest-demand packages first:

- `godot-project-doctor`
- `godot-asset-pipeline-doctor`
- `godot-export-preset-doctor`
- `godot-mobile-perf-doctor`

Then publish the remaining packages once the first feedback cycle is complete.

## Godot community outreach

Start with focused examples rather than broad claims:

- "CI check for Godot export presets before an Android release."
- "Find mobile-unfriendly textures and import settings."
- "Generate a PR artifact summarizing Godot production risks."
- "Use JSON/SARIF output so coding agents can act on findings."

Good places to share after release:

- Godot forum tooling category.
- Godot subreddit.
- Relevant Discord communities.
- Indie developer devlogs where CI tooling is welcome.

## Evidence to collect

- First external issue.
- First external project using the GitHub Action.
- First bugfix release based on user feedback.
- PyPI download trend after release.
- Example CI run link from a public repository.
- Mentions or testimonials from Godot developers.
