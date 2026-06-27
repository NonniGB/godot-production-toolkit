# Tiny Mobile Release

Use this path when a small Godot project needs Android/export, input, mobile UI,
localization, visual-smoke, and dashboard evidence before a release branch is
reviewed.

## Source Inputs

- Godot fixture: [`examples/release-readiness-demo`](../../release-readiness-demo/README.md)
- Localization fixture: [`godot-localization-qa-guard/examples/tiny-godot-project`](../../../godot-localization-qa-guard/examples/tiny-godot-project)
- Mobile UI metadata: [`examples/godot-exporters/fixtures/mobile-ui.json`](../../godot-exporters/fixtures/mobile-ui.json)
- Visual-smoke plan: [`godot-visual-smoke-test-kit/examples/visual-smoke.toml`](../../../godot-visual-smoke-test-kit/examples/visual-smoke.toml)
- Sample reports: [`docs/assets/sample-reports`](../../../docs/assets/sample-reports/README.md)

## Commands

Run from the repository root after installing the local packages you need:

```powershell
godot-project-doctor run examples\release-readiness-demo\godot-project-doctor.toml --format markdown --output docs\assets\sample-reports\release-readiness-summary.md
godot-mobile-ui-doctor readiness examples\godot-exporters\fixtures\mobile-ui.json --input-report docs\assets\sample-reports\input-map.json --export-report docs\assets\sample-reports\export.json --mobile-perf-report docs\assets\sample-reports\mobile-perf.json --format markdown --output docs\assets\sample-reports\mobile-ui.md
godot-l10n-guard stress-pack godot-localization-qa-guard\examples\tiny-godot-project --translations godot-localization-qa-guard\examples\tiny-godot-project\translations --output-dir docs\assets\sample-reports\localization-stress --format markdown --output docs\assets\sample-reports\localization-stress.md
godot-mobile-ui-doctor layout-risk examples\godot-exporters\fixtures\mobile-ui.json --stress-pack docs\assets\sample-reports\localization-stress\stress-pack-manifest.json --format markdown --output docs\assets\sample-reports\mobile-ui-layout-risk.md
godot-visual-smoke plan godot-visual-smoke-test-kit\examples\visual-smoke.toml --project examples\release-readiness-demo --format json --output reports\visual-plan.json
godot-release-dashboard build docs\assets\sample-reports --title "Tiny Mobile Release" --output docs\assets\sample-reports\release-dashboard-demo.html
```

## Report Snapshots

- [`release-readiness-summary.md`](../../../docs/assets/sample-reports/release-readiness-summary.md)
- [`mobile-ui.md`](../../../docs/assets/sample-reports/mobile-ui.md)
- [`mobile-ui-layout-risk.md`](../../../docs/assets/sample-reports/mobile-ui-layout-risk.md)
- [`localization-stress.md`](../../../docs/assets/sample-reports/localization-stress.md)
- [`release-dashboard-demo.html`](../../../docs/assets/sample-reports/release-dashboard-demo.html)
- Terminal capture: [`project-doctor-terminal.png`](../../../docs/assets/screenshots/project-doctor-terminal.png)
- Dashboard screenshot: [`release-dashboard-demo.png`](../../../docs/assets/screenshots/release-dashboard-demo.png)
