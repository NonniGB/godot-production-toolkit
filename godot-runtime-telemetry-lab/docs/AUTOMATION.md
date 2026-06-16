# Automation

Generate a CI-friendly runtime report:

```powershell
godot-telemetry-lab summarize reports\runtime --format json --output reports\runtime.json
```

Create a reusable budget file for the target you are testing:

```powershell
godot-telemetry-lab budget init --profile android-high --output reports\runtime-budget.json
```

Compare a release candidate with a saved baseline:

```powershell
godot-telemetry-lab compare reports\baseline-runtime reports\current-runtime --budget-file reports\runtime-budget.json --format markdown --output reports\runtime-compare.md
```

Write an HTML artifact that can be uploaded from CI:

```powershell
godot-telemetry-lab timeline reports\runtime --budget-file reports\runtime-budget.json --format html --output reports\runtime-timeline.html
godot-telemetry-lab timeline reports\runtime --budget-file reports\runtime-budget.json --format svg --output reports\runtime-timeline.svg
```

Exit codes:

- `0`: no findings at the selected fail threshold.
- `1`: findings met the selected fail threshold.
- `2`: command-line usage error.
