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
| Godot localization screenshot capture plan | `python -m pip install godot-localization-qa-guard` | `godot-l10n-guard capture-plan . --stress-pack reports/localization-stress/stress-pack-manifest.json --screen main_menu --viewport portrait_phone --format markdown` |
| Godot input map audit | `python -m pip install godot-input-map-auditor` | `godot-input-audit . --require keyboard,touch,controller --format markdown` |
| Godot visual regression test | `python -m pip install godot-visual-smoke-test-kit` | `godot-visual-smoke compare baseline current --diff reports/diff.png --format json` |
| Godot save fixture generation | `python -m pip install godot-save-schema-guard` | `godot-save-guard generate-fixture --schema schemas/save.schema.json --fixture-output saves/fixtures/generated.json --set 'player.id="pilot-1"'` |
| Godot save schema validation | `python -m pip install godot-save-schema-guard` | `godot-save-guard validate saves/fixtures --schema schemas/save.schema.json` |
| Godot save migration path check | `python -m pip install godot-save-schema-guard` | `godot-save-guard migration-graph --chain migrations.toml --current 3 --supported 1 --supported 2 --format markdown` |
| Godot save migration output validation | `python -m pip install godot-save-schema-guard` | `godot-save-guard migrate-chain saves/v1 --chain migrations.toml --output-dir reports/migrated-saves --schema schemas/save.schema.json --compare-original --format json` |
| Godot save fixture redaction | `python -m pip install godot-save-schema-guard` | `godot-save-guard redact saves/fixtures --path player.name --output-dir sanitized-saves --dry-run` |
| Godot scene signal audit | `python -m pip install godot-scene-signal-auditor` | `godot-signal-audit . --format json` |
| Godot scene contract check for nodes, groups, signals, handlers, and exported properties before refactoring | `python -m pip install godot-scene-signal-auditor` | `godot-signal-audit . --contract scene-contract.json --format json` |
| Godot scene contract diff after refactoring | `python -m pip install godot-scene-signal-auditor` | `godot-signal-audit . --contract scene-contract.json --baseline-contract previous-scene-contract.json --format json --fail-on none` |
| GDScript architecture boundary check | `python -m pip install godot-gdscript-architecture-guard` | `godot-architecture-guard . --config architecture-guard.toml --format markdown` |
| GDScript module owner, high fan-in/fan-out, and possible unused script/resource review | `python -m pip install godot-gdscript-architecture-guard` | `godot-architecture-guard . --config architecture-guard.toml --format markdown --fail-on none` |
| GDScript API comment coverage | `python -m pip install gdscript-api-comment-coverage` | `gdscript-api-coverage . --format markdown` |
| Godot data/content graph validation | `python -m pip install godot-content-graph-doctor` | `godot-content-graph . --preset recipes --format markdown` |
| Godot pack manifest generation from a folder | `python -m pip install godot-pack-mod-doctor` | `godot-pack-mod-doctor manifest from-folder addons/demo_pack --id demo_pack --version 1.0.0 --output pack-manifest.json` |
| Godot mod, DLC, or patch manifest check | `python -m pip install godot-pack-mod-doctor` | `godot-pack-mod-doctor check pack-manifest.json --format markdown` |
| Godot mod or DLC pack diff with moved-resource review | `python -m pip install godot-pack-mod-doctor` | `godot-pack-mod-doctor diff baseline-pack.json current-pack.json --format markdown` |
| Godot mod load order or missing dependency check | `python -m pip install godot-pack-mod-doctor` | `godot-pack-mod-doctor load-order base-pack.json patch-pack.json optional-mod.json --format markdown` |
| Godot restricted content-pack security check | `python -m pip install godot-pack-mod-doctor` | `godot-pack-mod-doctor security pack-manifest.json --format json` |
| Godot scenario evidence report | `python -m pip install godot-scenario-report-kit` | `godot-scenario-report manifest coverage scenario-manifest.json --results reports/current --format html` |
| Godot JUnit XML scenario summary | `python -m pip install godot-scenario-report-kit` | `godot-scenario-report summarize reports/junit.xml --format markdown` |
| Godot retried scenario summary | `python -m pip install godot-scenario-report-kit` | `godot-scenario-report flake compare reports/retry-run --format markdown` |
| Godot scenario evidence bundle | `python -m pip install godot-scenario-report-kit` | `godot-scenario-report bundle reports/scenarios --telemetry reports/runtime-timeline.json --visual reports/visual.json --evidence log=reports/run.log --format json` |
| Godot runtime telemetry timeline | `python -m pip install godot-runtime-telemetry-lab` | `godot-telemetry-lab timeline reports/runtime --format html --output reports/runtime-timeline.html` |
| Godot runtime telemetry baseline compare for frame and memory regressions | `python -m pip install godot-runtime-telemetry-lab` | `godot-telemetry-lab compare reports/baseline reports/current --format markdown` |
| Godot runtime telemetry adapter for Performance monitor CSV | `python -m pip install godot-runtime-telemetry-lab` | `godot-telemetry-lab adapt reports/godot-monitor.csv --format json --output reports/runtime-normalized.json` |
| Godot workflow-filtered release dashboard with typed highlights, scenario retry cards, export artifact cards, and previous-run readiness trends | `python -m pip install godot-release-dashboard-kit` | `godot-release-dashboard build reports/current --previous-reports-dir reports/previous --output reports/dashboard.html` |
| Pixel-art asset import and texture checks | `python -m pip install godot-asset-pipeline-doctor` | `godot-asset-doctor . --profile pixel-2d --format json` |
| Pixel space asset previews and image diffs | `python -m pip install pixel-space-asset-toolkit` | `pixel-space-assets compare-dir baseline current --diff-output-dir reports/pixel-diffs` |

## Profile Package Sets

Use these when `godot-project-doctor doctor . --profile <name> --write-plan`
is your starting point from a source checkout.

| Profile | Install | Covers |
|---|---|---|
| `release` | `python -m pip install godot-export-preset-doctor godot-asset-pipeline-doctor godot-input-map-auditor godot-localization-qa-guard godot-mobile-perf-doctor` | Export presets, asset imports, input map coverage, localization, and static mobile performance. |
| `android` | `python -m pip install godot-export-preset-doctor godot-mobile-perf-doctor godot-input-map-auditor godot-asset-pipeline-doctor godot-localization-qa-guard` | Android export settings, static mobile performance, input coverage, asset imports, and localization basics. |
| `html5` | `python -m pip install godot-export-preset-doctor godot-asset-pipeline-doctor godot-input-map-auditor godot-localization-qa-guard godot-visual-smoke-test-kit` | Web export settings, asset imports, input coverage, localization, and visual smoke planning. |
| `mobile` | `python -m pip install godot-export-preset-doctor godot-mobile-perf-doctor godot-input-map-auditor godot-mobile-ui-doctor godot-visual-smoke-test-kit` | Android/export readiness, mobile performance, touch/input coverage, mobile UI metadata, and visual smoke planning. |
| `mobile-ui` | `python -m pip install godot-input-map-auditor godot-mobile-ui-doctor godot-localization-qa-guard godot-visual-smoke-test-kit godot-mobile-perf-doctor` | Touch input, mobile UI metadata, localization, visual smoke planning, and mobile settings. |
| `localization` | `python -m pip install godot-localization-qa-guard godot-mobile-ui-doctor godot-visual-smoke-test-kit godot-input-map-auditor` | Translation files, mobile layout metadata, visual smoke planning, and input text flows. |
| `runtime` | `python -m pip install godot-scenario-report-kit godot-runtime-telemetry-lab godot-mobile-perf-doctor godot-visual-smoke-test-kit godot-scene-signal-auditor` | Scenario reports, runtime telemetry, static performance checks, visual smoke planning, and signal evidence. |
| `content` | `python -m pip install godot-content-graph-doctor godot-save-schema-guard godot-scenario-report-kit godot-pack-mod-doctor godot-asset-pipeline-doctor` | Content graph checks, save fixtures/schema checks, scenario evidence, pack manifests, and asset import review. |
| `save-migration` | `python -m pip install godot-save-schema-guard godot-scenario-report-kit godot-content-graph-doctor godot-runtime-telemetry-lab` | Save fixtures, schema validation, migration evidence, scenario reports, and content reference checks. |
| `mods` | `python -m pip install godot-pack-mod-doctor godot-content-graph-doctor godot-scenario-report-kit godot-asset-pipeline-doctor godot-save-schema-guard` | Pack manifests, content graph checks, scenario evidence, asset imports, and save compatibility inputs. |
| `architecture` | `python -m pip install godot-gdscript-architecture-guard godot-scene-signal-auditor gdscript-api-comment-coverage godot-scenario-report-kit` | GDScript module boundaries, scene signals, public API comments, and scenario evidence. |
| `visual` | `python -m pip install godot-visual-smoke-test-kit godot-mobile-ui-doctor godot-asset-pipeline-doctor godot-localization-qa-guard godot-input-map-auditor` | Screenshot plans, UI metadata, asset imports, localization stress inputs, and input coverage. |
| `qa` | `python -m pip install godot-scenario-report-kit godot-visual-smoke-test-kit godot-mobile-ui-doctor godot-gdscript-architecture-guard godot-scene-signal-auditor` | Scenario evidence, screenshot checks, mobile UI reports, architecture checks, and scene signal review. |

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
  or capture plans for layout review.
- Start with `godot-visual-smoke-test-kit` when screenshots need a repeatable
  baseline/diff/approval flow.
- Start with `godot-scenario-report-kit` and `godot-runtime-telemetry-lab` when
  test runs already produce JSON or CSV evidence and you want reviewable
  summaries, timelines, normalized Godot Performance monitor samples, or compact
  visual/log evidence summaries.
- Start with `godot-release-dashboard-kit` when a release or pull request has
  several reports, typed summary highlights, scenario retry evidence, and
  export artifact checks or screenshots that should be reviewed in one
  filterable static page.
- Start with `godot-scene-signal-auditor --contract` when a refactor should
  preserve specific nodes, groups, signal handlers, exported script properties,
  or scene-level script signals. Add `--baseline-contract` when reviewers need
  to see which scene contract requirements were removed from a previous
  contract.

For combined workflows, use the [Workflow Finder](search-index.md) or the
[Tool Index](TOOL_INDEX.md).
