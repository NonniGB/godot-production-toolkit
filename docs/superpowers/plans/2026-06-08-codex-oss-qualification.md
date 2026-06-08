# Codex OSS Qualification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the local Godot/pixel tool suite in `C:\Temp\tools` into a publishable open-source maintenance project with coherent tooling, agent-friendly automation, documentation, CI, and release evidence strong enough to apply for Codex for Open Source once organic usage exists.

**Architecture:** Keep the ten existing tools standalone, then add one umbrella CLI (`godot-project-doctor`) that orchestrates them without making them inseparable. Add one GitHub Action wrapper (`godot-ci-doctor-action`) so maintainers can use the suite in CI with JSON, SARIF, Markdown, and HTML artifacts. Strengthen each existing tool with `--version`, stable metadata, report schemas where practical, and public documentation that avoids private project examples.

**Tech Stack:** Python 3.11, argparse, unittest/pytest-compatible tests, Pillow where already required, GitHub composite actions, Markdown docs, static HTML report generation, JSON/SARIF outputs.

---

## Source Criteria

Official OpenAI source checked on 2026-06-08: `https://openai.com/form/codex-for-oss/`.

The programme looks for maintainers of active OSS projects with meaningful usage, broad adoption, or clear ecosystem importance, and evidence of active maintenance such as PR review, issue triage, release management, security, and quality work. The implementation below cannot force public usage, but it can make the project credible, useful, maintainable, discoverable, and ready to collect those signals.

## File Structure

- Create: `C:\Temp\tools\godot-project-doctor\` for the umbrella CLI package.
- Create: `C:\Temp\tools\godot-ci-doctor-action\` for the reusable GitHub Action.
- Create: `C:\Temp\tools\.github\workflows\portfolio-ci.yml` for monorepo validation.
- Create: `C:\Temp\tools\.github\ISSUE_TEMPLATE\*.yml` and `C:\Temp\tools\.github\pull_request_template.md`.
- Create: `C:\Temp\tools\docs\CODEx_FOR_OSS_READINESS.md` for application-readiness evidence and gap tracking.
- Create: `C:\Temp\tools\docs\PUBLICATION_GUIDE.md` for GitHub, PyPI, and Godot-community release steps.
- Modify: each existing tool `src\*\cli.py` to support `--version`.
- Modify: selected high-value tools to add SARIF output: `godot-asset-pipeline-doctor`, `godot-input-map-auditor`, `godot-localization-qa-guard`, `godot-mobile-perf-doctor`.
- Modify: root `README.md`, `IMPLEMENTATION_STATUS.md`, `AGENTIC_INTERFACE_REVIEW.md`, and every affected tool README.

## Task 1: Root Repository Foundation

**Files:**
- Create: `C:\Temp\tools\.gitignore`
- Create: `C:\Temp\tools\pyproject.toml`
- Create: `C:\Temp\tools\.github\workflows\portfolio-ci.yml`
- Create: `C:\Temp\tools\.github\ISSUE_TEMPLATE\bug_report.yml`
- Create: `C:\Temp\tools\.github\ISSUE_TEMPLATE\feature_request.yml`
- Create: `C:\Temp\tools\.github\pull_request_template.md`
- Modify: `C:\Temp\tools\README.md`

- [ ] **Step 1: Add monorepo validation script tests**

Create root tests that execute `verify_agent_interfaces.py`, check every tool has `README.md`, `LICENSE`, `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md`, `pyproject.toml`, `agent-tool.json`, and confirm no private project name appears in public files.

- [ ] **Step 2: Run the failing repository-quality checks**

Run:

```powershell
python C:\Temp\tools\verify_agent_interfaces.py
python -m pytest C:\Temp\tools\tests -q
```

Expected before implementation: missing `C:\Temp\tools\tests` or failing repository-quality tests.

- [ ] **Step 3: Add root packaging and CI metadata**

Add a root `pyproject.toml` for dev tooling, `.gitignore`, GitHub workflow, issue templates, and PR template. CI must validate manifests, run all ten existing test suites, run new umbrella/action tests, and scan for private references.

- [ ] **Step 4: Re-run validation**

Run:

```powershell
python C:\Temp\tools\verify_agent_interfaces.py
python -m pytest C:\Temp\tools\tests -q
```

Expected after implementation: all root checks pass.

## Task 2: Universal CLI Version Support

**Files:**
- Modify: each existing `C:\Temp\tools\*\src\*\cli.py`
- Modify: each existing `C:\Temp\tools\*\tests\test_cli.py` or add a small version test
- Modify: each existing `C:\Temp\tools\*\README.md`

- [ ] **Step 1: Write version tests**

For each CLI, add a test that calls `main(["--version"])`, expects exit code `0`, and asserts the package name plus `0.1.0` appears in stdout.

- [ ] **Step 2: Run representative failing tests**

Run each package test suite with:

```powershell
python -m pytest C:\Temp\tools\<tool>\tests -q
```

Expected before implementation: `--version` is rejected or missing.

- [ ] **Step 3: Add version flags**

Use `parser.add_argument("--version", action="version", version="<script-name> 0.1.0")` in every CLI, matching each `pyproject.toml` script name.

- [ ] **Step 4: Re-run all ten suites**

Run:

```powershell
Get-ChildItem C:\Temp\tools -Directory | Where-Object { Test-Path (Join-Path $_.FullName 'tests') } | ForEach-Object { python -m pytest (Join-Path $_.FullName 'tests') -q }
```

Expected after implementation: all existing and new version tests pass.

## Task 3: Umbrella CLI `godot-project-doctor`

**Files:**
- Create: `C:\Temp\tools\godot-project-doctor\pyproject.toml`
- Create: `C:\Temp\tools\godot-project-doctor\README.md`
- Create: `C:\Temp\tools\godot-project-doctor\LICENSE`
- Create: `C:\Temp\tools\godot-project-doctor\CHANGELOG.md`
- Create: `C:\Temp\tools\godot-project-doctor\CONTRIBUTING.md`
- Create: `C:\Temp\tools\godot-project-doctor\SECURITY.md`
- Create: `C:\Temp\tools\godot-project-doctor\agent-tool.json`
- Create: `C:\Temp\tools\godot-project-doctor\src\godot_project_doctor\__init__.py`
- Create: `C:\Temp\tools\godot-project-doctor\src\godot_project_doctor\cli.py`
- Create: `C:\Temp\tools\godot-project-doctor\src\godot_project_doctor\runner.py`
- Create: `C:\Temp\tools\godot-project-doctor\src\godot_project_doctor\reports.py`
- Create: `C:\Temp\tools\godot-project-doctor\tests\test_cli.py`
- Create: `C:\Temp\tools\godot-project-doctor\examples\godot-project-doctor.toml`

- [ ] **Step 1: Write failing orchestration tests**

Test `plan` returns the exact commands for enabled tools, `run --dry-run --format json` emits machine-readable planned checks, and `summarize` merges sample JSON reports into one summary with totals by severity.

- [ ] **Step 2: Run failing umbrella tests**

Run:

```powershell
python -m pytest C:\Temp\tools\godot-project-doctor\tests -q
```

Expected before implementation: package/import errors.

- [ ] **Step 3: Implement runner and reports**

Implement an explicit tool registry, config parser using `tomllib`, subprocess runner with timeout support, JSON report merger, Markdown summary, and static HTML summary. Do not execute external tools unless the user calls `run`; `plan` and `run --dry-run` must be side-effect free.

- [ ] **Step 4: Add documentation and manifest**

Document standalone CLI usage, agent-safe JSON usage, CI usage, config examples, exit codes, and how to disable checks that are not relevant to a project.

- [ ] **Step 5: Re-run umbrella tests**

Run:

```powershell
python -m pytest C:\Temp\tools\godot-project-doctor\tests -q
```

Expected after implementation: all umbrella tests pass.

## Task 4: GitHub Action `godot-ci-doctor-action`

**Files:**
- Create: `C:\Temp\tools\godot-ci-doctor-action\action.yml`
- Create: `C:\Temp\tools\godot-ci-doctor-action\README.md`
- Create: `C:\Temp\tools\godot-ci-doctor-action\LICENSE`
- Create: `C:\Temp\tools\godot-ci-doctor-action\CHANGELOG.md`
- Create: `C:\Temp\tools\godot-ci-doctor-action\CONTRIBUTING.md`
- Create: `C:\Temp\tools\godot-ci-doctor-action\SECURITY.md`
- Create: `C:\Temp\tools\godot-ci-doctor-action\agent-tool.json`
- Create: `C:\Temp\tools\godot-ci-doctor-action\tests\test_action_metadata.py`

- [ ] **Step 1: Write action metadata tests**

Assert `action.yml` is a composite action, exposes `project`, `config`, `reports-dir`, and `fail-on` inputs, uploads or writes JSON/Markdown/HTML/SARIF artifacts, and calls `godot-project-doctor`.

- [ ] **Step 2: Run failing action tests**

Run:

```powershell
python -m pytest C:\Temp\tools\godot-ci-doctor-action\tests -q
```

Expected before implementation: missing action metadata.

- [ ] **Step 3: Implement the composite action**

Use `actions/setup-python`, install `godot-project-doctor`, run `godot-project-doctor run`, and expose report paths as outputs. Keep the default noninteractive and network-light after package installation.

- [ ] **Step 4: Add copy-paste workflow docs**

Document minimal usage, strict CI usage, artifact upload, SARIF upload, and local reproduction commands.

- [ ] **Step 5: Re-run action tests**

Run:

```powershell
python -m pytest C:\Temp\tools\godot-ci-doctor-action\tests -q
```

Expected after implementation: all action metadata tests pass.

## Task 5: SARIF and HTML Reporting Upgrades

**Files:**
- Modify: `C:\Temp\tools\godot-asset-pipeline-doctor\src\godot_asset_doctor\*`
- Modify: `C:\Temp\tools\godot-input-map-auditor\src\godot_input_auditor\*`
- Modify: `C:\Temp\tools\godot-localization-qa-guard\src\godot_l10n_guard\*`
- Modify: `C:\Temp\tools\godot-mobile-perf-doctor\src\godot_mobile_perf_doctor\*`
- Add tests under each package `tests\`

- [ ] **Step 1: Write SARIF tests**

For each selected tool, run the CLI with `--format sarif`, parse stdout or output file as JSON, and assert SARIF `version`, `runs[0].tool.driver.name`, `rules`, and `results` exist.

- [ ] **Step 2: Run failing SARIF tests**

Expected before implementation: unsupported `sarif` format.

- [ ] **Step 3: Implement compact SARIF emitters**

Map existing findings to SARIF rules/results without adding new dependencies. Preserve existing JSON/text/Markdown behavior.

- [ ] **Step 4: Add umbrella HTML report**

Use `godot-project-doctor summarize --format html` to render a static report with severity totals, per-tool sections, command metadata, and links to generated artifacts.

- [ ] **Step 5: Re-run selected package and umbrella tests**

Expected after implementation: SARIF and HTML tests pass.

## Task 6: Public Documentation and Qualification Evidence

**Files:**
- Create: `C:\Temp\tools\docs\CODEx_FOR_OSS_READINESS.md`
- Create: `C:\Temp\tools\docs\PUBLICATION_GUIDE.md`
- Create: `C:\Temp\tools\docs\MAINTAINER_AUTOMATION.md`
- Modify: `C:\Temp\tools\README.md`
- Modify: `C:\Temp\tools\IMPLEMENTATION_STATUS.md`

- [ ] **Step 1: Write docs checks**

Root tests should verify the docs exist and include install, local validation, release process, application evidence, issue triage, maintainer automation, and adoption metrics sections.

- [ ] **Step 2: Add readiness docs**

Document current strengths, remaining public-usage gap, release checklist, suggested first issues, support policy, and the 500-character application-field drafts without claiming guaranteed eligibility.

- [ ] **Step 3: Re-run docs checks**

Expected after implementation: root docs checks pass.

## Task 7: End-to-End Review and Publication

**Files:**
- Modify: `C:\Temp\tools\IMPLEMENTATION_STATUS.md`
- Modify: `C:\Temp\tools\docs\CODEx_FOR_OSS_READINESS.md`
- Initialize: git repository in `C:\Temp\tools`
- Publish: public GitHub repository through the connected GitHub plugin or `gh` fallback where the plugin lacks local git operations

- [ ] **Step 1: Run full local verification**

Run:

```powershell
python C:\Temp\tools\verify_agent_interfaces.py
Get-ChildItem C:\Temp\tools -Directory | Where-Object { Test-Path (Join-Path $_.FullName 'tests') } | ForEach-Object { python -m pytest (Join-Path $_.FullName 'tests') -q }
python -m pytest C:\Temp\tools\tests -q
```

Expected after implementation: manifests pass, tests pass, and the root repository contract test reports no private-project reference matches.

- [ ] **Step 2: Review qualification state**

Update `CODEx_FOR_OSS_READINESS.md` with the honest status: technically credible and maintained-looking, still dependent on real public usage/adoption before application strength is high.

- [ ] **Step 3: Initialize git and commit**

Run noninteractive git commands only after verification passes:

```powershell
git -C C:\Temp\tools init
git -C C:\Temp\tools add .
git -C C:\Temp\tools commit -m "feat: publish godot production tooling suite"
```

- [ ] **Step 4: Publish to GitHub**

Use the GitHub plugin first for repository publication where available. Use `gh repo create`/`git push` only for gaps the connector does not cover. Repository should be public, have a clear description, and include all docs and examples.

- [ ] **Step 5: Final report**

Report the GitHub URL, verification results, remaining public-adoption gap, and concrete next outreach/release steps.
