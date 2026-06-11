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
```

When a project already uses `godot-visual-smoke-test-kit`, reuse its viewport
plan instead of duplicating phone and tablet sizes:

```powershell
godot-visual-smoke plan visual-smoke.toml --project . --format json --output reports\visual-plan.json
godot-mobile-ui-doctor matrix mobile-ui.json --visual-smoke-plan reports\visual-plan.json --format markdown --output reports\mobile-ui-matrix.md
godot-mobile-ui-doctor overlays mobile-ui.json --visual-smoke-plan reports\visual-plan.json --output-dir reports\mobile-ui-overlays
```

The command exits with:

- `0` when no findings meet the selected fail threshold;
- `1` when findings meet the selected fail threshold;
- `2` for CLI or metadata errors.
