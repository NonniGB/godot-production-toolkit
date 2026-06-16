# Automation

Generate a CI-friendly runtime report:

```powershell
godot-telemetry-lab summarize reports\runtime --format json --output reports\runtime.json
```

Compare a release candidate with a saved baseline:

```powershell
godot-telemetry-lab compare reports\baseline-runtime reports\current-runtime --format markdown --output reports\runtime-compare.md
```

Exit codes:

- `0`: no findings at the selected fail threshold.
- `1`: findings met the selected fail threshold.
- `2`: command-line usage error.
