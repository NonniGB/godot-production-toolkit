# Tool Index

Start here by release workflow or review task. Each tool can run locally or in
CI, and most standalone tools are available from PyPI.

## Good First Workflows

### Android Release

```powershell
godot-export-doctor . --format json --output reports/export.json
godot-export-doctor matrix . --expected-platform Android --expected-platform Web --format markdown --output reports/export-matrix.md
godot-export-doctor leaks . --format html --output reports/export-leaks.html --fail-on none
godot-mobile-perf-doctor . --static --format markdown --output reports/mobile-perf.md
godot-asset-doctor . --profile mobile --format json --output reports/assets.json
```

### Mobile UI And Input Review

```powershell
godot-input-audit . --require keyboard,touch --format markdown --output reports/input-map.md
godot-mobile-ui-doctor matrix mobile-ui.json --format markdown --output reports/mobile-ui-matrix.md
godot-mobile-ui-doctor overlays mobile-ui.json --output-dir reports/mobile-ui-overlays --fail-on none
godot-mobile-ui-doctor readiness mobile-ui.json --input-report reports/input-map.json --export-report reports/export.json --mobile-perf-report reports/mobile-perf.json --format markdown --output reports/mobile-readiness.md
```

### Localization Review

```powershell
godot-l10n-guard . --translations translations --require fr,es --scan-scripts --format markdown --output reports/localization.md
godot-mobile-ui-doctor readiness mobile-ui.json --localization-report reports/localization.json --format markdown --output reports/localized-ui-readiness.md
```

### Visual Regression

```powershell
godot-visual-smoke plan visual-smoke.toml --project . --format json --output reports/visual-plan.json
godot-visual-smoke compare screenshots/baseline/menu.png screenshots/current/menu.png --diff reports/visual-diffs/menu.png --format json --output reports/visual-smoke.json
```

### Save Migration

```powershell
godot-save-guard validate saves/fixtures --schema schemas/save.schema.json --format markdown --output reports/save-validation.md
```

### Runtime Performance

```powershell
godot-telemetry-lab budget init --profile android-high --output reports/runtime-budget.json
godot-telemetry-lab timeline reports/runtime --budget-file reports/runtime-budget.json --format html --output reports/runtime-timeline.html
```

### Content And Mod Packs

```powershell
godot-content-graph . --preset recipes --format markdown --output reports/content-graph.md --fail-on none
godot-pack-mod-doctor check pack-manifest.json --base base-content.json --format markdown --output reports/pack.md
```

### Release Evidence Dashboard

```powershell
godot-project-doctor doctor . --profile release
godot-project-doctor run --project . --checks assets,export,input,localization,signals,mobile_perf --format json --output reports/godot-project-doctor/summary.json
godot-release-dashboard build reports --output reports/dashboard.html
```

## Start By Problem

| Problem | Use | Typical command |
|---|---|---|
| Android, desktop, or web export settings are hard to review | `godot-export-preset-doctor`, `godot-mobile-perf-doctor` | `godot-export-doctor matrix . --expected-platform Android --expected-platform Web --format markdown` |
| Godot mobile UI needs safe-area and touch-target checks | `godot-mobile-ui-doctor` | `godot-mobile-ui-doctor readiness mobile-ui.json --format markdown` |
| Screenshots need regression testing | `godot-visual-smoke-test-kit` | `godot-visual-smoke compare baseline current --format json` |
| Imported PNGs, pixel art, icons, or sprite anchors need review | `godot-asset-pipeline-doctor` | `godot-asset-doctor . --profile pixel-2d --format json` |
| Input actions need keyboard, mouse, touch, and controller coverage | `godot-input-map-auditor` | `godot-input-audit . --format markdown` |
| CSV or PO localization imports need QA | `godot-localization-qa-guard` | `godot-l10n-guard . --format markdown` |
| Save data needs schema and migration checks | `godot-save-schema-guard` | `godot-save-guard validate fixtures --schema save.schema.json` |
| Scene refactors risk broken signal wiring | `godot-scene-signal-auditor` | `godot-signal-audit . --format json` |
| GDScript modules or autoload access are becoming tangled | `godot-gdscript-architecture-guard` | `godot-architecture-guard . --config architecture-guard.toml` |
| Data files reference missing ids, recipes, quests, or levels | `godot-content-graph-doctor` | `godot-content-graph . --preset recipes --format markdown` |
| Runtime scenario runs need manifests, coverage, flake checks, or baseline comparison | `godot-scenario-report-kit` | `godot-scenario-report manifest coverage scenario-manifest.json --results reports/current --format html` |
| Runtime telemetry needs budgets, timelines, or baseline comparison | `godot-runtime-telemetry-lab` | `godot-telemetry-lab timeline reports/runtime --format html --output reports/runtime-timeline.html` |
| Pack, patch, DLC, or mod manifests need release checks | `godot-pack-mod-doctor` | `godot-pack-mod-doctor check pack-manifest.json --format markdown` |
| Release reports and screenshots need one static review page | `godot-release-dashboard-kit` | `godot-release-dashboard build reports --output reports/dashboard.html` |
| Public GDScript APIs need comment coverage | `gdscript-api-comment-coverage` | `gdscript-api-coverage . --format markdown` |
| Pixel-art space assets need deterministic previews or PNG diffs | `pixel-space-asset-toolkit` | `pixel-space-assets compare-dir baseline current --diff-output-dir reports/pixel-diffs` |
| Several checks need one report | `godot-project-doctor` | `godot-project-doctor summarize reports --format html` |
| A first-run checklist is needed for release, mobile, content, or QA work | `godot-project-doctor` | `godot-project-doctor doctor . --profile release` |

## Package Names

| Package | CLI | Main output |
|---|---|---|
| `gdscript-api-comment-coverage` | `gdscript-api-coverage` | JSON, Markdown |
| `godot-asset-pipeline-doctor` | `godot-asset-doctor` | JSON, SARIF, PNG previews |
| `godot-content-graph-doctor` | `godot-content-graph` | JSON, Markdown, Mermaid |
| `godot-export-preset-doctor` | `godot-export-doctor` | JSON, SARIF, Markdown, HTML |
| `godot-gdscript-architecture-guard` | `godot-architecture-guard` | JSON, SARIF, Markdown, Mermaid |
| `godot-input-map-auditor` | `godot-input-audit` | JSON, SARIF, Markdown |
| `godot-localization-qa-guard` | `godot-l10n-guard` | JSON, SARIF, Markdown |
| `godot-mobile-perf-doctor` | `godot-mobile-perf-doctor` | JSON, SARIF, Markdown |
| `godot-mobile-ui-doctor` | `godot-mobile-ui-doctor` | JSON, Markdown, PNG |
| `godot-pack-mod-doctor` | `godot-pack-mod-doctor` | JSON, Markdown, text |
| `godot-release-dashboard-kit` | `godot-release-dashboard` | HTML, JSON |
| `godot-runtime-telemetry-lab` | `godot-telemetry-lab` | JSON, Markdown, text, HTML, SVG |
| `godot-save-schema-guard` | `godot-save-guard` | JSON, Markdown |
| `godot-scenario-report-kit` | `godot-scenario-report` | JSON, Markdown, HTML |
| `godot-scene-signal-auditor` | `godot-signal-audit` | JSON, Mermaid |
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
- `*.csv`, `*.po`, `*.pot`: localization QA.
- `content/`, `data/`, `resources/`: data graph and content reference checks.
- `reports/`: combined summaries, scenario results, screenshot diffs, and CI artifacts.
