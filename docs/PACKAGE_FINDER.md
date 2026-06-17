# Package Finder

Use this page when you want one focused package instead of the full checkout.
Each package is a small command-line tool for a specific Godot production check.

## Quick Picks

| Search phrase | Install | Run |
|---|---|---|
| Godot Android export preset check | `python -m pip install godot-export-preset-doctor` | `godot-export-doctor matrix . --expected-platform Android --format markdown` |
| Godot export leak or debug file check | `python -m pip install godot-export-preset-doctor` | `godot-export-doctor leaks . --format html --output reports/export-leaks.html` |
| Godot export preset diff | `python -m pip install godot-export-preset-doctor` | `godot-export-doctor diff . --baseline reports/baseline-export-presets --format markdown` |
| Godot exported folder or file-list inspection | `python -m pip install godot-export-preset-doctor` | `godot-export-doctor inspect-folder build/android --hash-files --format json --output reports/exported-folder.json` |
| Godot mobile performance static check | `python -m pip install godot-mobile-perf-doctor` | `godot-mobile-perf-doctor . --static --format markdown` |
| Godot mobile UI safe area check | `python -m pip install godot-mobile-ui-doctor` | `godot-mobile-ui-doctor readiness mobile-ui.json --format markdown` |
| Godot mobile UI localization expansion check | `python -m pip install godot-mobile-ui-doctor godot-localization-qa-guard` | `godot-mobile-ui-doctor layout-risk mobile-ui.json --stress-pack reports/localization-stress/stress-pack-manifest.json --format markdown` |
| Godot mobile UI overlay with localization markers | `python -m pip install godot-mobile-ui-doctor godot-localization-qa-guard` | `godot-mobile-ui-doctor overlays mobile-ui.json --layout-risk-report reports/mobile-layout-risk.json --output-dir reports/mobile-ui-overlays` |
| Godot localization QA | `python -m pip install godot-localization-qa-guard` | `godot-l10n-guard . --translations translations --format markdown` |
| Godot localization stress pack or text overflow review | `python -m pip install godot-localization-qa-guard` | `godot-l10n-guard stress-pack . --translations translations --output-dir reports/localization-stress --format markdown` |
| Godot input map audit | `python -m pip install godot-input-map-auditor` | `godot-input-audit . --require keyboard,touch,controller --format markdown` |
| Godot visual regression test | `python -m pip install godot-visual-smoke-test-kit` | `godot-visual-smoke compare baseline current --diff reports/diff.png --format json` |
| Godot save fixture generation | `python -m pip install godot-save-schema-guard` | `godot-save-guard generate-fixture --schema schemas/save.schema.json --fixture-output saves/fixtures/generated.json --set 'player.id="pilot-1"'` |
| Godot save schema validation | `python -m pip install godot-save-schema-guard` | `godot-save-guard validate saves/fixtures --schema schemas/save.schema.json` |
| Godot save migration path check | `python -m pip install godot-save-schema-guard` | `godot-save-guard migration-graph --chain migrations.toml --current 3 --supported 1 --supported 2 --format markdown` |
| Godot save migration output validation | `python -m pip install godot-save-schema-guard` | `godot-save-guard migrate-chain saves/v1 --chain migrations.toml --output-dir reports/migrated-saves --schema schemas/save.schema.json --format json` |
| Godot save fixture redaction | `python -m pip install godot-save-schema-guard` | `godot-save-guard redact saves/fixtures --path player.name --output-dir sanitized-saves --dry-run` |
| Godot scene signal audit | `python -m pip install godot-scene-signal-auditor` | `godot-signal-audit . --format json` |
| Godot scene contract check before refactoring | `python -m pip install godot-scene-signal-auditor` | `godot-signal-audit . --contract scene-contract.json --format json` |
| GDScript architecture boundary check | `python -m pip install godot-gdscript-architecture-guard` | `godot-architecture-guard . --config architecture-guard.toml --format markdown` |
| GDScript API comment coverage | `python -m pip install gdscript-api-comment-coverage` | `gdscript-api-coverage . --format markdown` |
| Godot data/content graph validation | `python -m pip install godot-content-graph-doctor` | `godot-content-graph . --preset recipes --format markdown` |
| Godot pack manifest generation from a folder | `python -m pip install godot-pack-mod-doctor` | `godot-pack-mod-doctor manifest from-folder addons/demo_pack --id demo_pack --version 1.0.0 --output pack-manifest.json` |
| Godot mod, DLC, or patch manifest check | `python -m pip install godot-pack-mod-doctor` | `godot-pack-mod-doctor check pack-manifest.json --format markdown` |
| Godot mod or DLC pack diff with moved-resource review | `python -m pip install godot-pack-mod-doctor` | `godot-pack-mod-doctor diff baseline-pack.json current-pack.json --format markdown` |
| Godot mod load order or missing dependency check | `python -m pip install godot-pack-mod-doctor` | `godot-pack-mod-doctor load-order base-pack.json patch-pack.json optional-mod.json --format markdown` |
| Godot scenario evidence report | `python -m pip install godot-scenario-report-kit` | `godot-scenario-report manifest coverage scenario-manifest.json --results reports/current --format html` |
| Godot scenario evidence bundle | `python -m pip install godot-scenario-report-kit` | `godot-scenario-report bundle reports/scenarios --telemetry reports/runtime-timeline.json --visual reports/visual.json --evidence log=reports/run.log --format json` |
| Godot runtime telemetry timeline | `python -m pip install godot-runtime-telemetry-lab` | `godot-telemetry-lab timeline reports/runtime --format html --output reports/runtime-timeline.html` |
| Godot runtime telemetry adapter | `python -m pip install godot-runtime-telemetry-lab` | `godot-telemetry-lab adapt reports/godot-monitor.csv --format json --output reports/runtime-normalized.json` |
| Godot release dashboard | `python -m pip install godot-release-dashboard-kit` | `godot-release-dashboard build reports --output reports/dashboard.html` |
| Pixel-art asset import and texture checks | `python -m pip install godot-asset-pipeline-doctor` | `godot-asset-doctor . --profile pixel-2d --format json` |
| Pixel space asset previews and image diffs | `python -m pip install pixel-space-asset-toolkit` | `pixel-space-assets compare-dir baseline current --diff-output-dir reports/pixel-diffs` |

## Which Package Should I Start With?

- Start with `godot-export-preset-doctor` for export failures, release target
  drift, Android package identifiers, debug flags, broad export filters, and
  local-looking paths in `export_presets.cfg`. It can also inspect exported
  folders or generated file lists for development-looking or private files.
- Start with `godot-mobile-ui-doctor` for portrait UI, safe areas, small touch
  targets, crowded controls, localization expansion risk, and exported
  `Control` rectangle metadata.
- Start with `godot-localization-qa-guard` for CSV/PO translation checks,
  missing keys, placeholder mismatches, script key usage, and stress catalogs
  for layout review.
- Start with `godot-visual-smoke-test-kit` when screenshots need a repeatable
  baseline/diff/approval flow.
- Start with `godot-scenario-report-kit` and `godot-runtime-telemetry-lab` when
  test runs already produce JSON evidence and you want reviewable summaries.
- Start with `godot-release-dashboard-kit` when a release or pull request has
  several reports and screenshots that should be reviewed in one static page.
- Start with `godot-scene-signal-auditor --contract` when a refactor should
  preserve specific nodes, signal handlers, or scene-level script signals.

For combined workflows, use the [Workflow Finder](search-index.md) or the
[Tool Index](TOOL_INDEX.md).
