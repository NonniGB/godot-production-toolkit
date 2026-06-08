# Agentic And Standalone Interface Review

Date: 2026-06-08

## Summary

The ten tools are usable as standalone Python CLI packages, but the first pass had three common gaps:

1. Agent discovery was implicit. An agent had to read prose docs and infer commands, output formats, write behavior, and exit-code semantics.
2. Visual or generative tools had weaker machine-readable status surfaces than the audit tools.
3. Interface guidance was split across READMEs and docs, without a suite-level contract.

This hardening pass adds a stable `agent-tool.json` manifest to every tool, a root `agent-interface.schema.json`, and `verify_agent_interfaces.py` to check the manifests. It also adds JSON/status output for `pixel-space-assets` generation commands, JSON plan output for `godot-visual-smoke plan`, an umbrella runner, a GitHub Action wrapper, and neutral project metadata.

## Implemented Fixes

- Added `agent-tool.json` to each tool folder.
- Added `agent-interface.schema.json` at the suite root.
- Added `verify_agent_interfaces.py` for local/CI validation of manifest presence and required fields.
- Added `pixel-space-assets --format json` status output for `starfield`, `asteroid-hex`, `strip-background`, and `preview`.
- Added `godot-visual-smoke plan --format json` for command planning without parsing shell text.
- Added a static gallery entry point for `pixel-space-asset-toolkit`.
- Updated relevant README examples for agent-safe JSON usage.
- Added `godot-project-doctor` for one-command planning, dry-runs, execution, and JSON/Markdown/HTML summaries.
- Added `godot-ci-doctor-action` for GitHub Actions adoption.
- Added SARIF to asset, input, localization, and mobile performance diagnostics.
- Added `PROJECT_OVERVIEW.md` and `project-metadata.json`.

## Tool-by-Tool Assessment

| Tool | Standalone CLI | Machine Output | Human Interface | Agentic Notes |
|---|---:|---:|---|---|
| `godot-project-doctor` | yes | JSON | text/Markdown/HTML | Umbrella CLI for planning and summaries. |
| `godot-ci-doctor-action` | n/a | JSON/SARIF artifacts | Markdown/HTML artifacts | GitHub Actions adoption path. |
| `godot-asset-pipeline-doctor` | yes | JSON/SARIF | text/docs | Strong CI and code scanning fit. |
| `godot-export-preset-doctor` | yes | JSON/SARIF | text/docs | Strong release gate. Later add env-secret allow/deny config. |
| `gdscript-api-comment-coverage` | yes | JSON | API Markdown | Strong maintainability gate. Later improve multiline GDScript parsing. |
| `godot-input-map-auditor` | yes | JSON/SARIF | Markdown/GDScript constants | Good standalone docs generator. Later add action groups config. |
| `godot-localization-qa-guard` | yes | JSON/SARIF | Markdown report | Useful release QA. Later add ignore lists for intentionally dynamic keys. |
| `godot-save-schema-guard` | yes | JSON | Markdown report | Useful compatibility gate. Later add migration dry-run and post-migration schema validation. |
| `godot-scene-signal-auditor` | yes | JSON | Mermaid graph | Good architecture visibility. Later resolve more dynamic script attachments. |
| `godot-visual-smoke-test-kit` | yes | JSON | PNG diff images | Needs project-owned Godot capture helper for full end-to-end use. Plan output is now agent-readable. |
| `godot-mobile-perf-doctor` | yes | JSON/SARIF | Markdown report | Strong mobile release usefulness. Later integrate export preset checks and real adb capture. |
| `pixel-space-asset-toolkit` | yes | JSON status/manifests | PNG gallery/previews | Now suitable for agent generation loops. Later add parameter presets and HTML gallery generation command. |

## Interface Standard

Every tool should keep these behaviors:

- Noninteractive by default.
- No network access required.
- JSON output for agents and CI.
- Text or Markdown output for humans.
- Writes only when an explicit output path, docs path, generation output, or approval command is supplied.
- Exit `0` for success, exit `1` for findings at the selected threshold, and exit `2` for CLI usage errors.
- Redact secrets and avoid embedding private project examples in public docs.

## Remaining Build-Out Recommendations

Highest value next:

1. Add per-tool config files for ignore lists, rule severity overrides, and output defaults.
2. Add a simple HTML report for visual smoke diffs and pixel asset galleries.
3. Add dry-run support for commands that may execute external processes, especially `godot-save-guard migrate`.
4. Add JSON schema files for each report format once the output stabilizes.
5. Publish packages in stages and use real issue feedback to guide priorities.

## Publication Notes

For the first release, publish as one umbrella repository so users can see the suite, CI, action, and maintenance model together. If packages later split into separate repositories, keep each folder's `agent-tool.json` at the repository root.
