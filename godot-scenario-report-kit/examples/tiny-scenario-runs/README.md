# Tiny Scenario Runs

This fixture has a passing baseline and a current run with one regression. It is
small enough to understand without running Godot.

```powershell
godot-scenario-report summarize current --format markdown
godot-scenario-report compare baseline current --format markdown
godot-scenario-report manifest check scenario-manifest.json --results current --format markdown
godot-scenario-report manifest coverage scenario-manifest.json --results current --format html --output scenario-coverage.html
godot-scenario-report flake compare baseline current repeat-run --format markdown
```

The manifest lists the scenarios expected for a small release check, the tags
and critical flows they cover, and the artifacts the runner should have written.
`repeat-run` is intentionally inconsistent so `flake compare` has a status
change to report.
