# Automation

Summarize a directory of scenario JSON files:

```powershell
godot-scenario-report summarize reports\scenarios --format json --output reports\scenarios\summary.json
```

Compare against a previous run:

```powershell
godot-scenario-report compare reports\baseline reports\current --format html --output reports\scenario-compare.html
```

The tool is runner-neutral. Any Godot test harness can emit the small JSON shape
described in the README.

