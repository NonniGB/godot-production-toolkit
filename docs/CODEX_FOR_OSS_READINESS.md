# Codex For Open Source Readiness

## Technical readiness

The suite now has twelve agent-facing projects: ten standalone tools, one umbrella CLI, and one GitHub Action. The tools are installable Python CLIs or action metadata, have tests, documentation, examples, changelogs, security notes, contribution notes, and agent manifests.

High-value readiness signals:

- `godot-project-doctor` can plan, dry-run, run, and summarize checks.
- `godot-ci-doctor-action` gives other repositories a copy-paste CI path.
- JSON output supports agents and dashboards.
- SARIF output exists for the tools most useful in GitHub code scanning: assets, input, localization, and mobile performance.
- Static HTML and Markdown summaries make results easy to review without a custom service.

## Maintenance evidence

Repository-level maintenance material includes:

- `.github/workflows/portfolio-ci.yml`
- `.github/ISSUE_TEMPLATE/bug_report.yml`
- `.github/ISSUE_TEMPLATE/feature_request.yml`
- `.github/pull_request_template.md`
- `SECURITY.md` in each tool folder
- `CONTRIBUTING.md` in each tool folder
- `CHANGELOG.md` in each tool folder
- `agent-tool.json` in each agent-facing project
- `verify_agent_interfaces.py`
- `AI_REVIEW_PACKAGE.md`
- `oss-review-evidence.json`

## Adoption gap

The adoption gap is real and should be disclosed. The project cannot yet show organic public usage until it has been published and used by people outside the local development environment.

Evidence to collect after publication:

- GitHub stars, forks, issues, and pull requests.
- External projects using `godot-ci-doctor-action`.
- PyPI downloads for the most useful packages.
- Godot forum, Reddit, Discord, or Mastodon mentions.
- Issues closed with fixes and release notes.
- Security or compatibility reports handled transparently.

## Application draft

Short project description:

> Godot Production Toolkit is a suite of CI-friendly, agent-readable diagnostics for Godot 4 projects. It helps indie developers catch export, asset, input, localization, signal, save compatibility, visual smoke, and mobile performance risks before release.

Why it matters:

> The project targets a narrow but repeatable tooling gap in the Godot ecosystem: production readiness checks that are lightweight enough for solo developers and structured enough for coding agents and CI.

Current honest status:

> The project is technically prepared for public release with tests, docs, GitHub Action support, JSON/SARIF outputs, and maintainer workflows. The remaining gap is organic public usage, which should be gathered after publication.
