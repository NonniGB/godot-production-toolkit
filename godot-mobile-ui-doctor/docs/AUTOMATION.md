# Automation

`godot-mobile-ui-doctor` is designed for CI and local scripts:

```powershell
godot-mobile-ui-doctor mobile-ui.json --format json --output reports\mobile-ui.json
```

Use `--fail-on warning` when touch-target or layout risks should block a pull
request. Use `--fail-on error` when adopting the tool gradually.

For a compact review artifact:

```powershell
godot-mobile-ui-doctor matrix mobile-ui.json --format markdown --output reports\mobile-ui-matrix.md
```

For visual PR artifacts, render PNG overlays from the same metadata:

```powershell
godot-mobile-ui-doctor overlays mobile-ui.json --output-dir reports\mobile-ui-overlays --fail-on none
godot-mobile-ui-doctor overlays mobile-ui.json --screenshot-dir reports\screenshots --output-dir reports\mobile-ui-overlays --fail-on none
```

Screenshot-backed overlays expect files named `screen__viewport.png` or
`screen.png`. This lets screenshot capture jobs and metadata exporters feed the
same review artifact.

To bring related mobile checks into one review artifact:

```powershell
godot-mobile-ui-doctor readiness mobile-ui.json --input-report reports\input-map.json --export-report reports\export.json --localization-report reports\localization.json --mobile-perf-report reports\mobile-perf.json --format markdown --output reports\mobile-readiness.md
```

For localization-sensitive UI, generate stress catalogs before the project
captures its UI metadata:

```powershell
godot-l10n-guard stress-pack . --translations translations --output-dir reports\localization-stress
godot-mobile-ui-doctor layout-risk mobile-ui.json --stress-pack reports\localization-stress\stress-pack-manifest.json --format markdown --output reports\mobile-layout-risk.md
```

Use the stress catalogs in a project-owned UI capture step when possible. The
joined `layout-risk` report is useful even before screenshot capture because it
matches translation keys or source text to exported control rectangles.

The readiness report includes the linked reports' top findings and grouped rule
counts in addition to the per-screen mobile UI matrix, which makes it suitable
for pull-request artifacts and CI summaries.

When a project already uses `godot-visual-smoke-test-kit`, reuse its viewport
plan instead of duplicating phone and tablet sizes:

```powershell
godot-visual-smoke plan visual-smoke.toml --project . --format json --output reports\visual-plan.json
godot-mobile-ui-doctor matrix mobile-ui.json --visual-smoke-plan reports\visual-plan.json --format markdown --output reports\mobile-ui-matrix.md
godot-mobile-ui-doctor overlays mobile-ui.json --visual-smoke-plan reports\visual-plan.json --output-dir reports\mobile-ui-overlays
godot-mobile-ui-doctor readiness mobile-ui.json --visual-smoke-plan reports\visual-plan.json --visual-smoke-report reports\visual-plan.json --format markdown --output reports\mobile-readiness.md
```

The command exits with:

- `0` when no findings meet the selected fail threshold;
- `1` when findings meet the selected fail threshold;
- `2` for CLI or metadata errors.
