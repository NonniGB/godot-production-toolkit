# Workflow Guides

Start here when you know the release or review task, but not the package name.
Each guide lists the usual inputs, one or two commands, and the report artifact
to keep from a local run or CI job.

| Workflow | Use when | Main inputs | Useful output |
|---|---|---|---|
| [Android export CI](godot-android-export-ci.md) | Android release presets, package identity, ABIs, icons, or signing placeholders need review. | `export_presets.cfg`, `project.godot`, optional asset imports. | SARIF, JSON, Markdown, or HTML export reports. |
| [HTML5 web export checklist](godot-html5-web-export-checklist.md) | A browser build needs preset, asset, and visual smoke checks. | `export_presets.cfg`, web export folder, screenshots. | Export report plus optional screenshot diff artifacts. |
| [Release checklist](godot-ci-release-checklist.md) | A pull request or release branch needs a compact production preflight. | Godot project folder and optional tool config. | `godot-project-doctor` summary and dashboard inputs. |
| [Mobile UI safe-area testing](godot-mobile-ui-safe-area-testing.md) | Portrait/touch UI needs safe-area, touch-target, spacing, or overlay review. | `mobile-ui.json`, optional screenshots. | Markdown readiness report and PNG overlays. |
| [Localization overflow testing](godot-localization-overflow-testing.md) | Translated text may break placeholders, keys, or visible layout. | CSV/PO files, scripts, optional UI metadata. | Localization QA report, stress catalogs, layout-risk report, and optional overlay PNGs. |
| [Visual regression testing](godot-visual-regression-testing.md) | Menus, HUDs, scenes, or exports need screenshot comparison. | Baseline/current PNG folders or capture plan. | JSON report and PNG diffs. |
| [Scene contract refactor safety](godot-scene-contract-refactor-safety.md) | Scene/node/signal refactors need a small API contract before review. | `.tscn`, `.gd`, optional contract JSON/TOML. | Signal report and contract violations. |
| [Save migration testing](godot-save-migration-testing.md) | Save format changes need fixture and migration proof. | Save fixtures and JSON schema. | Save compatibility report. |
| [Runtime performance regression](godot-runtime-performance-regression.md) | Scenario runs emit frame, memory, draw-call, or phase samples. | Runtime telemetry JSON or CSV. | Budget summary, baseline comparison, or timeline report. |
| [Mod and DLC pack validation](godot-mod-dlc-pack-validation.md) | Pack, patch, DLC, or mod manifests need release checks. | Pack manifest and optional base manifest. | Pack validation report. |
| [Godot version upgrade checks](godot-version-upgrade-checks.md) | A Godot 4.x upgrade branch needs before/after evidence. | Toolkit reports, screenshots, content data, save fixtures. | Upgrade comparison report and visual diffs. |

For a package-by-package command map, use the [Tool Index](../TOOL_INDEX.md).
For practical search phrases, use the [Workflow Finder](../search-index.md).
