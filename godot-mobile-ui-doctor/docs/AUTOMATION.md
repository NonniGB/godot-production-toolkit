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

The command exits with:

- `0` when no findings meet the selected fail threshold;
- `1` when findings meet the selected fail threshold;
- `2` for CLI or metadata errors.
