# Tool Index

This page maps common Godot 4 production problems to the command-line tools in
this repository. Each tool can run locally or in CI, and most standalone tools
are available from PyPI.

## Start By Problem

| Problem | Use | Typical command |
|---|---|---|
| Android export settings are hard to review | `godot-export-preset-doctor`, `godot-mobile-perf-doctor` | `godot-export-doctor . --format sarif --output reports/export.sarif` |
| Godot mobile UI needs safe-area and touch-target checks | `godot-mobile-ui-doctor` | `godot-mobile-ui-doctor readiness mobile-ui.json --format markdown` |
| Screenshots need regression testing | `godot-visual-smoke-test-kit` | `godot-visual-smoke compare baseline current --format json` |
| Imported PNGs, pixel art, icons, or sprite anchors need review | `godot-asset-pipeline-doctor` | `godot-asset-doctor . --profile pixel-2d --format json` |
| Input actions need keyboard, mouse, touch, and controller coverage | `godot-input-map-auditor` | `godot-input-audit . --format markdown` |
| CSV or PO localization imports need QA | `godot-localization-qa-guard` | `godot-l10n-guard . --format markdown` |
| Save data needs schema and migration checks | `godot-save-schema-guard` | `godot-save-guard validate fixtures --schema save.schema.json` |
| Scene refactors risk broken signal wiring | `godot-scene-signal-auditor` | `godot-signal-audit . --format json` |
| GDScript modules or autoload access are becoming tangled | `godot-gdscript-architecture-guard` | `godot-architecture-guard . --config architecture-guard.toml` |
| Data files reference missing ids, recipes, quests, or levels | `godot-content-graph-doctor` | `godot-content-graph . --preset recipes --format markdown` |
| Runtime scenario runs need a readable summary or baseline comparison | `godot-scenario-report-kit` | `godot-scenario-report compare baseline current --format markdown` |
| Runtime telemetry needs budget or baseline comparison | `godot-runtime-telemetry-lab` | `godot-telemetry-lab compare baseline current --format markdown` |
| Pack, patch, DLC, or mod manifests need release checks | `godot-pack-mod-doctor` | `godot-pack-mod-doctor check pack-manifest.json --format markdown` |
| Release reports and screenshots need one static review page | `godot-release-dashboard-kit` | `godot-release-dashboard build reports --output reports/dashboard.html` |
| Public GDScript APIs need comment coverage | `gdscript-api-comment-coverage` | `gdscript-api-coverage . --format markdown` |
| Pixel-art space assets need deterministic previews or PNG diffs | `pixel-space-asset-toolkit` | `pixel-space-assets compare-dir baseline current --diff-output-dir reports/pixel-diffs` |
| Several checks need one report | `godot-project-doctor` | `godot-project-doctor summarize reports --format html` |

## Package Names

| Package | CLI | Main output |
|---|---|---|
| `gdscript-api-comment-coverage` | `gdscript-api-coverage` | JSON, Markdown |
| `godot-asset-pipeline-doctor` | `godot-asset-doctor` | JSON, SARIF, PNG previews |
| `godot-content-graph-doctor` | `godot-content-graph` | JSON, Markdown, Mermaid |
| `godot-export-preset-doctor` | `godot-export-doctor` | JSON, SARIF |
| `godot-gdscript-architecture-guard` | `godot-architecture-guard` | JSON, SARIF, Markdown, Mermaid |
| `godot-input-map-auditor` | `godot-input-audit` | JSON, SARIF, Markdown |
| `godot-localization-qa-guard` | `godot-l10n-guard` | JSON, SARIF, Markdown |
| `godot-mobile-perf-doctor` | `godot-mobile-perf-doctor` | JSON, SARIF, Markdown |
| `godot-mobile-ui-doctor` | `godot-mobile-ui-doctor` | JSON, Markdown, PNG |
| `godot-pack-mod-doctor` | `godot-pack-mod-doctor` | JSON, Markdown, text |
| `godot-release-dashboard-kit` | `godot-release-dashboard` | HTML, JSON |
| `godot-runtime-telemetry-lab` | `godot-telemetry-lab` | JSON, Markdown, text |
| `godot-save-schema-guard` | `godot-save-guard` | JSON, Markdown |
| `godot-scenario-report-kit` | `godot-scenario-report` | JSON, Markdown, HTML |
| `godot-scene-signal-auditor` | `godot-signal-audit` | JSON, Mermaid |
| `godot-visual-smoke-test-kit` | `godot-visual-smoke` | JSON, PNG diffs |
| `pixel-space-asset-toolkit` | `pixel-space-assets` | JSON, PNG, HTML |

## Good First Workflows

### Android Release Preflight

```powershell
godot-export-doctor . --format json --output reports/export.json
godot-mobile-perf-doctor . --static --format markdown --output reports/mobile-perf.md
godot-asset-doctor . --profile mobile --format json --output reports/assets.json
```

### Mobile UI Review

```powershell
godot-mobile-ui-doctor matrix mobile-ui.json --format markdown --output reports/mobile-ui-matrix.md
godot-mobile-ui-doctor overlays mobile-ui.json --output-dir reports/mobile-ui-overlays --fail-on none
godot-mobile-ui-doctor readiness mobile-ui.json --input-report reports/input-map.json --export-report reports/export.json --mobile-perf-report reports/mobile-perf.json --format markdown --output reports/mobile-readiness.md
```

### Pull Request Report

```powershell
godot-project-doctor run --project . --checks assets,export,input,localization,signals,mobile_perf --format json --output reports/godot-project-doctor/summary.json
godot-project-doctor summarize reports/godot-project-doctor --format html --output reports/godot-project-doctor/index.html
```

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
