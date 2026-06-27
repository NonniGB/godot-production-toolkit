# Tiny Content Game

Use this path when content data, save fixtures, scenario runs, and pack/mod
manifests need review together.

## Source Inputs

- Content data: [`godot-content-graph-doctor/examples/tiny-content-project`](../../../godot-content-graph-doctor/examples/tiny-content-project/README.md)
- Pack manifest: [`examples/godot-exporters/fixtures/pack-manifest.json`](../../godot-exporters/fixtures/pack-manifest.json)
- Save schema and fixtures: [`godot-save-schema-guard/examples`](../../../godot-save-schema-guard/examples)
- Scenario runs: [`godot-scenario-report-kit/examples/tiny-scenario-runs`](../../../godot-scenario-report-kit/examples/tiny-scenario-runs/README.md)
- Sample reports: [`docs/assets/sample-reports`](../../../docs/assets/sample-reports/README.md)

## Commands

Run from the repository root after installing the local packages you need:

```powershell
godot-content-graph godot-content-graph-doctor\examples\tiny-content-project --config godot-content-graph-doctor\examples\tiny-content-project\content-graph.toml --format markdown --output docs\assets\sample-reports\content-graph-summary.md
godot-pack-mod-doctor check examples\godot-exporters\fixtures\pack-manifest.json --format json --output docs\assets\sample-reports\pack-mod.json
godot-pack-mod-doctor security examples\godot-exporters\fixtures\pack-manifest.json --format json --output docs\assets\sample-reports\pack-mod-security.json
godot-save-guard validate godot-save-schema-guard\examples\fixtures --schema godot-save-schema-guard\examples\schema\save.schema.json --format markdown --output docs\assets\sample-reports\save-fixture-generation.md --fail-on none
godot-save-guard migrate-chain godot-save-schema-guard\examples\fixtures\v1 --chain godot-save-schema-guard\examples\migrations\chain.toml --output-dir reports\generated-save-migrations --schema godot-save-schema-guard\examples\schema\save.schema.json --compare-original --format json --output docs\assets\sample-reports\save-migration-comparison.json
godot-scenario-report summarize godot-scenario-report-kit\examples\tiny-scenario-runs\current --format markdown --output docs\assets\sample-reports\scenario-junit-summary.md
```

## Report Snapshots

- [`content-graph-summary.md`](../../../docs/assets/sample-reports/content-graph-summary.md)
- [`pack-mod.json`](../../../docs/assets/sample-reports/pack-mod.json)
- [`pack-mod-security.json`](../../../docs/assets/sample-reports/pack-mod-security.json)
- [`save-fixture-generation.md`](../../../docs/assets/sample-reports/save-fixture-generation.md)
- [`save-migration-comparison.json`](../../../docs/assets/sample-reports/save-migration-comparison.json)
- [`scenario-junit-summary.md`](../../../docs/assets/sample-reports/scenario-junit-summary.md)
- Terminal capture: [`content-graph-terminal.svg`](../../../docs/assets/screenshots/content-graph-terminal.svg)
