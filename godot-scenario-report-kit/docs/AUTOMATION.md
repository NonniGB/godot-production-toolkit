# Automation

Summarize a directory of scenario JSON files:

```powershell
godot-scenario-report summarize reports\scenarios --format json --output reports\scenarios\summary.json
```

Compare against a previous run:

```powershell
godot-scenario-report compare reports\baseline reports\current --format html --output reports\scenario-compare.html
```

Validate the scenario suite that was expected to run:

```powershell
godot-scenario-report manifest check scenario-manifest.json --results reports\current --format json --output reports\scenario-manifest.json
godot-scenario-report manifest coverage scenario-manifest.json --results reports\current --format html --output reports\scenario-coverage.html
```

Compare repeated runs before trusting a newly passing suite:

```powershell
godot-scenario-report flake compare reports\run-1 reports\run-2 reports\run-3 --format markdown --output reports\scenario-flakes.md
```

Build a review bundle for PR or release artifacts:

```powershell
godot-scenario-report bundle reports\scenarios --manifest scenario-manifest.json --evidence log=reports\run.log --evidence junit=reports\junit.xml --format json --output reports\scenario-bundle.json
```

The tool is runner-neutral. Any Godot test harness can emit the small JSON shape
described in the README.
