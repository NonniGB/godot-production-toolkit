# Tiny Scenario Runs

This fixture has a passing baseline and a current run with one regression. It is
small enough to understand without running Godot.

```powershell
godot-scenario-report summarize current --format markdown
godot-scenario-report summarize junit.xml --format markdown
godot-scenario-report compare baseline current --format markdown
godot-scenario-report manifest check scenario-manifest.json --results current --format markdown
godot-scenario-report manifest coverage scenario-manifest.json --results current --format html --output scenario-coverage.html
godot-scenario-report flake compare baseline current repeat-run --format markdown
godot-scenario-report flake compare retry-run --format markdown
godot-scenario-report bundle current --manifest scenario-manifest.json --visual visual-smoke.json --evidence log=run.log --evidence junit=junit.xml --format markdown
```

The manifest lists the scenarios expected for a small release check, the tags
and critical flows they cover, and the artifacts the runner should have written.
`repeat-run` is intentionally inconsistent so `flake compare` has a status
change to report. `retry-run` records two attempts of the same scenario in one
file, which is useful for checking how retried runs are summarized.

`junit.xml` is a tiny runner-style example. It can be summarized directly, or
linked into a bundle as review evidence beside the JSON scenario results.

`visual-smoke.json` is a compact screenshot-comparison style report. Bundle
reports summarize it without copying screenshot files, so the resulting JSON,
Markdown, or HTML can point reviewers at the visual evidence that belongs with a
scenario run.
