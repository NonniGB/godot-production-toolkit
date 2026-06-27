# Tool Index

Start here by release workflow or review task. The toolkit is organized around
maintainer evidence for Godot CI and release review: exports, mobile readiness,
localization, save migrations, runtime telemetry, screenshots, and release
dashboards.
Each tool can run locally or in CI, and most standalone tools are available
from PyPI.

If you already know the problem and only need a package name, install command,
profile package set, and first command, use the [Package Finder](PACKAGE_FINDER.md).

## Workflow Lanes

| Lane | Use it for | Primary packages |
|---|---|---|
| Project and release evidence | First-pass audits, PR reports, dashboards, and release checklist runs. | `godot-production-doctor`, `godot-ci-doctor-action`, `godot-release-dashboard-action`, `godot-release-dashboard-kit` |
| Export and mobile readiness | Export presets, build folders, Android/mobile settings, texture risks, safe areas, and touch layout. | `godot-export-preset-doctor`, `godot-mobile-perf-doctor`, `godot-mobile-ui-doctor`, `godot-asset-pipeline-doctor` |
| UI, input, localization, and visuals | Input maps, translated text, touch readiness, screenshot plans, and visual diffs. | `godot-input-map-auditor`, `godot-localization-qa-guard`, `godot-visual-smoke-test-kit`, `pixel-space-asset-toolkit` |
| Runtime and scenario evidence | Scenario result summaries, JUnit XML, flakes, retries, telemetry budgets, and timelines. | `godot-scenario-report-kit`, `godot-runtime-telemetry-lab` |
| Data, saves, packs, and content | Content references, save fixtures, migrations, pack manifests, DLC/mod checks, and load order. | `godot-content-graph-doctor`, `godot-save-schema-guard`, `godot-pack-mod-doctor` |
| Code and scene refactor review | GDScript dependencies, scene contracts, signals, autoload coupling, and public API comments. | `godot-gdscript-architecture-guard`, `godot-scene-signal-auditor`, `gdscript-api-comment-coverage` |

## Good First Workflows

### Starter Project Audit

```powershell
godot-project-doctor run godot-project-doctor.toml --format markdown --output reports/starter-audit.md
godot-release-dashboard build reports/starter-audit --title "Starter Audit" --project "My Godot Project" --output reports/starter-audit-dashboard.html
```

### Android Release

```powershell
godot-export-doctor . --format json --output reports/export.json
godot-export-doctor matrix . --expected-platform Android --expected-platform Web --format markdown --output reports/export-matrix.md
godot-export-doctor diff . --baseline reports/baseline-export-presets --format markdown --output reports/export-diff.md --fail-on none
godot-export-doctor leaks . --format html --output reports/export-leaks.html --fail-on none
godot-export-doctor inspect-folder build/android --hash-files --format markdown --output reports/exported-folder.md --fail-on none
godot-export-doctor inspect-files reports/export-file-list.json --format markdown --output reports/exported-files.md --fail-on none
godot-export-doctor pck reports/export-file-list.json --format markdown --output reports/exported-pck.md --fail-on none
godot-mobile-perf-doctor . --static --mobile-ui-metadata reports/mobile-ui.json --format markdown --output reports/mobile-perf.md
godot-asset-doctor . --profile mobile --format json --output reports/assets.json
```

### Mobile UI And Input Review

```powershell
godot-input-audit . --require keyboard,touch --format markdown --output reports/input-map.md
godot-mobile-ui-doctor matrix mobile-ui.json --format markdown --output reports/mobile-ui-matrix.md
godot-mobile-ui-doctor overlays mobile-ui.json --output-dir reports/mobile-ui-overlays --fail-on none
godot-mobile-ui-doctor overlays mobile-ui.json --layout-risk-report reports/mobile-layout-risk.json --output-dir reports/mobile-ui-overlays --fail-on none
godot-mobile-ui-doctor readiness mobile-ui.json --input-report reports/input-map.json --export-report reports/export.json --mobile-perf-report reports/mobile-perf.json --format markdown --output reports/mobile-readiness.md
```

### Localization Review

```powershell
godot-l10n-guard . --translations translations --require fr,es --scan-scripts --format markdown --output reports/localization.md
godot-l10n-guard stress-pack . --translations translations --output-dir reports/localization-stress --format markdown --output reports/localization-stress.md
godot-l10n-guard capture-plan . --stress-pack reports/localization-stress/stress-pack-manifest.json --screen main_menu --screen settings --viewport portrait_phone --format markdown --output reports/localization-capture-plan.md
godot-mobile-ui-doctor layout-risk mobile-ui.json --stress-pack reports/localization-stress/stress-pack-manifest.json --format markdown --output reports/mobile-layout-risk.md
godot-mobile-ui-doctor layout-risk mobile-ui.json --stress-pack reports/localization-stress/stress-pack-manifest.json --format json --output reports/mobile-layout-risk.json
godot-mobile-ui-doctor overlays mobile-ui.json --layout-risk-report reports/mobile-layout-risk.json --output-dir reports/mobile-ui-overlays --fail-on none
godot-mobile-ui-doctor readiness mobile-ui.json --localization-report reports/localization.json --format markdown --output reports/localized-ui-readiness.md
```

### Visual Regression

```powershell
godot-visual-smoke plan visual-smoke.toml --project . --format json --output reports/visual-plan.json
godot-visual-smoke compare screenshots/baseline/menu.png screenshots/current/menu.png --diff reports/visual-diffs/menu.png --format json --output reports/visual-smoke.json
```

### Save Migration

```powershell
godot-save-guard generate-fixture --schema schemas/save.schema.json --fixture-output saves/fixtures/generated_v3.json --set 'player.id="pilot-1"' --format markdown --output reports/save-fixture-generation.md
godot-save-guard validate saves/fixtures --schema schemas/save.schema.json --format markdown --output reports/save-validation.md
godot-save-guard migration-graph --chain migrations.toml --current 3 --supported 1 --supported 2 --format markdown --output reports/save-migration-graph.md
godot-save-guard redact saves/fixtures --path player.name --path players.*.email --output-dir reports/sanitized-saves --dry-run --format markdown --output reports/save-redaction-plan.md
godot-save-guard migrate-chain saves/v1 --chain migrations.toml --output-dir reports/migrated-saves --schema schemas/save.schema.json --compare-original --format json --output reports/save-migration.json
```

### Runtime Performance

```powershell
godot-telemetry-lab budget init --profile android-high --output reports/runtime-budget.json
godot-telemetry-lab adapt reports/godot-monitor.csv --format json --output reports/runtime-normalized.json
godot-telemetry-lab timeline reports/runtime --budget-file reports/runtime-budget.json --format html --output reports/runtime-timeline.html
```

### Content And Mod Packs

```powershell
godot-content-graph . --preset recipes --format markdown --output reports/content-graph.md --fail-on none
godot-pack-mod-doctor manifest from-folder addons/demo_pack --id demo_pack --version 1.0.0 --output pack-manifest.json
godot-pack-mod-doctor check pack-manifest.json --base base-content.json --format markdown --output reports/pack.md
godot-pack-mod-doctor diff baseline-pack.json current-pack.json --format markdown --output reports/pack-diff.md
godot-pack-mod-doctor load-order base-pack.json patch-pack.json optional-mod.json --format markdown --output reports/pack-load-order.md
godot-pack-mod-doctor security pack-manifest.json --format json --output reports/pack-security.json
```

### Release Evidence Dashboard

```powershell
godot-project-doctor doctor . --profile release --write-plan
godot-project-doctor doctor . --profile android --write-plan
godot-project-doctor doctor . --profile runtime --write-plan
godot-project-doctor run --project . --checks assets,export,input,localization,signals,mobile_perf --format json --output reports/godot-project-doctor/summary.json
godot-release-dashboard build reports --output reports/dashboard.html
```

## Start By Problem

| Problem | Use | Typical command |
|---|---|---|
| Android, desktop, or web export settings are hard to review | `godot-export-preset-doctor`, `godot-mobile-perf-doctor` | `godot-export-doctor matrix . --expected-platform Android --expected-platform Web --format markdown` |
| Exported build folders, generated PCK manifests, or file lists need reviewable artifact checks | `godot-export-preset-doctor` | `godot-export-doctor pck reports/export-file-list.json --format markdown` |
| Godot mobile UI needs safe-area and touch-target checks | `godot-mobile-ui-doctor` | `godot-mobile-ui-doctor readiness mobile-ui.json --format markdown` |
| Godot mobile UI labels need localization expansion checks | `godot-mobile-ui-doctor`, `godot-localization-qa-guard` | `godot-mobile-ui-doctor layout-risk mobile-ui.json --stress-pack reports/localization-stress/stress-pack-manifest.json --format markdown` |
| Godot mobile UI overlays should show localized text risks | `godot-mobile-ui-doctor`, `godot-localization-qa-guard` | `godot-mobile-ui-doctor overlays mobile-ui.json --layout-risk-report reports/mobile-layout-risk.json --output-dir reports/mobile-ui-overlays` |
| Godot UI text needs pseudo, long, compact, or RTL-like stress catalogs | `godot-localization-qa-guard` | `godot-l10n-guard stress-pack . --translations translations --output-dir reports/localization-stress` |
| Godot localization screenshots need a locale and viewport checklist | `godot-localization-qa-guard` | `godot-l10n-guard capture-plan . --stress-pack reports/localization-stress/stress-pack-manifest.json --screen main_menu --viewport portrait_phone --format markdown` |
| Screenshots need regression testing | `godot-visual-smoke-test-kit` | `godot-visual-smoke compare baseline current --format json` |
| Imported PNGs, pixel art, icons, or sprite anchors need review | `godot-asset-pipeline-doctor` | `godot-asset-doctor . --profile pixel-2d --format json` |
| Input actions need keyboard, mouse, touch, and controller coverage | `godot-input-map-auditor` | `godot-input-audit . --format markdown` |
| CSV or PO localization imports need QA | `godot-localization-qa-guard` | `godot-l10n-guard . --format markdown` |
| Save fixtures need a baseline sample from the current schema | `godot-save-schema-guard` | `godot-save-guard generate-fixture --schema schemas/save.schema.json --fixture-output fixtures/generated.json` |
| Save data needs schema and migration checks | `godot-save-schema-guard` | `godot-save-guard validate fixtures --schema save.schema.json` |
| Supported save versions need migration path checks | `godot-save-schema-guard` | `godot-save-guard migration-graph --chain migrations.toml --current 3 --supported 1` |
| Migration commands should prove final saves match the current schema | `godot-save-schema-guard` | `godot-save-guard migrate-chain fixtures/v1 --chain migrations.toml --output-dir migrated --schema save.schema.json --compare-original` |
| Save fixtures need selected-field redaction before sharing | `godot-save-schema-guard` | `godot-save-guard redact fixtures --path player.name --output-dir sanitized-fixtures --dry-run` |
| Scene refactors risk broken signal wiring | `godot-scene-signal-auditor` | `godot-signal-audit . --format json` |
| Scene refactors need required nodes, groups, handlers, exported properties, or signals kept stable | `godot-scene-signal-auditor` | `godot-signal-audit . --contract scene-contract.json --format json` |
| Scene contract changes need before-and-after review | `godot-scene-signal-auditor` | `godot-signal-audit . --contract scene-contract.json --baseline-contract previous-scene-contract.json --format json --fail-on none` |
| GDScript modules, owner areas, autoload access, high fan-in/fan-out files, or stale resources are becoming tangled | `godot-gdscript-architecture-guard` | `godot-architecture-guard . --config architecture-guard.toml --format markdown --fail-on none` |
| Data files reference missing ids, recipes, quests, or levels | `godot-content-graph-doctor` | `godot-content-graph . --preset recipes --format markdown` |
| Runtime scenario runs need manifests, coverage, flake checks, retry grouping, JUnit XML summaries, visual/log evidence summaries, or baseline comparison | `godot-scenario-report-kit` | `godot-scenario-report manifest coverage scenario-manifest.json --results reports/current --format html` |
| Scenario runs, logs, screenshots, telemetry, and visual reports need one evidence manifest | `godot-scenario-report-kit` | `godot-scenario-report bundle reports/scenarios --telemetry reports/runtime-timeline.json --visual reports/visual.json --evidence log=reports/run.log --format json` |
| Runtime telemetry needs adapters, budgets, timelines, or frame/memory baseline comparison | `godot-runtime-telemetry-lab` | `godot-telemetry-lab compare reports/baseline reports/current --format markdown` |
| Pack, patch, DLC, or mod manifests need release checks | `godot-pack-mod-doctor` | `godot-pack-mod-doctor check pack-manifest.json --format markdown` |
| A pack folder needs a manifest before review or CI | `godot-pack-mod-doctor` | `godot-pack-mod-doctor manifest from-folder addons/demo_pack --id demo_pack --version 1.0.0 --output pack-manifest.json` |
| Pack updates need added/removed/changed/moved files or load-order conflicts reviewed | `godot-pack-mod-doctor` | `godot-pack-mod-doctor diff baseline-pack.json current-pack.json --format markdown` |
| Mod or DLC packs need missing dependency or ordering checks | `godot-pack-mod-doctor` | `godot-pack-mod-doctor load-order base-pack.json patch-pack.json optional-mod.json --format markdown` |
| User content packs should not include scripts, native libraries, archives, or packed projects | `godot-pack-mod-doctor` | `godot-pack-mod-doctor security pack-manifest.json --format json` |
| Release reports, scenario retries, export artifacts, and screenshots need one filterable static review page | `godot-release-dashboard-kit` | `godot-release-dashboard build reports --previous-reports-dir reports-previous --output reports/dashboard.html` |
| Public GDScript APIs need comment coverage | `gdscript-api-comment-coverage` | `gdscript-api-coverage . --format markdown` |
| Pixel-art space assets need deterministic previews or PNG diffs | `pixel-space-asset-toolkit` | `pixel-space-assets compare-dir baseline current --diff-output-dir reports/pixel-diffs` |
| Several checks need one report | `godot-production-doctor` | `godot-project-doctor summarize reports --format html` |
| A first-run checklist with package installs is needed for Android, web, localization, runtime evidence, mods, save migration, architecture, visual, mobile UI, release, content, or QA work | `godot-production-doctor` | `godot-project-doctor doctor . --profile android --write-plan` |

## Package Names

| Package | CLI | Main output |
|---|---|---|
| `gdscript-api-comment-coverage` | `gdscript-api-coverage` | JSON, Markdown |
| `godot-asset-pipeline-doctor` | `godot-asset-doctor` | JSON, SARIF, PNG previews |
| `godot-content-graph-doctor` | `godot-content-graph` | JSON, Markdown, Mermaid |
| `godot-export-preset-doctor` | `godot-export-doctor` | JSON, SARIF, Markdown, HTML |
| `godot-gdscript-architecture-guard` | `godot-architecture-guard` | JSON, SARIF, Markdown, Mermaid |
| `godot-input-map-auditor` | `godot-input-audit` | JSON, SARIF, Markdown |
| `godot-localization-qa-guard` | `godot-l10n-guard` | JSON, SARIF, Markdown, CSV |
| `godot-mobile-perf-doctor` | `godot-mobile-perf-doctor` | JSON, SARIF, Markdown, stretch checks, safe-area evidence handoff |
| `godot-mobile-ui-doctor` | `godot-mobile-ui-doctor` | JSON, Markdown, PNG |
| `godot-pack-mod-doctor` | `godot-pack-mod-doctor` | JSON, Markdown, text, rule metadata |
| `godot-production-doctor` | `godot-project-doctor` | JSON, Markdown, HTML, profile plans, combined reports |
| `godot-release-dashboard-kit` | `godot-release-dashboard` | Workflow-filtered HTML, JSON, typed highlights, scenario retry sections, export artifact sections, previous-run readiness trends |
| `godot-runtime-telemetry-lab` | `godot-telemetry-lab` | JSON, Markdown, text, HTML, SVG, normalized telemetry samples, frame/memory baseline deltas, rule metadata |
| `godot-save-schema-guard` | `godot-save-guard` | JSON, Markdown |
| `godot-scenario-report-kit` | `godot-scenario-report` | JSON, Markdown, HTML |
| `godot-scene-signal-auditor` | `godot-signal-audit` | JSON, Mermaid, contract diffs |
| `godot-visual-smoke-test-kit` | `godot-visual-smoke` | JSON, PNG diffs |
| `pixel-space-asset-toolkit` | `pixel-space-assets` | JSON, PNG, HTML |

## Focused Examples

### Pixel Asset Diff

```powershell
pixel-space-assets preview generated\ferric --columns 8 --cell-size 64 --output generated\ferric_preview.png
pixel-space-assets compare baseline\ferric_preview.png generated\ferric_preview.png --diff-output reports\ferric_diff.png --fail-on-diff --format json
pixel-space-assets compare-dir baseline\ferric generated\ferric --diff-output-dir reports\ferric_diffs --fail-on-diff --format json
```

## File Hints

- `project.godot`: input maps, display/mobile settings, renderer settings.
- `export_presets.cfg`: Android, desktop, and web export readiness.
- `*.import`: texture import flags and pixel-art filtering risks.
- `mobile-ui.json`: exported `Control` rectangles, text, touch targets, and safe areas.
- `*.csv`, `*.po`, `*.pot`: localization QA and stress-pack generation.
- `content/`, `data/`, `resources/`: data graph and content reference checks.
- `reports/`: combined summaries, scenario results, screenshot diffs, and CI artifacts.
