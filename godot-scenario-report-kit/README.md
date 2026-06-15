# Godot Scenario Report Kit

`godot-scenario-report-kit` validates and summarizes scenario run evidence from
Godot projects. It does not replace GUT, GdUnit4, custom runners, or editor
plugins. It gives those runs a small evidence format that is easier to compare
in CI and review artifacts.

## Install

```powershell
python -m pip install godot-scenario-report-kit
```

From a source checkout:

```powershell
python -m pip install -e .\godot-scenario-report-kit
```

## Quick Start

```powershell
godot-scenario-report summarize examples\tiny-scenario-runs\current --format markdown
```

Compare a baseline with a current run:

```powershell
godot-scenario-report compare examples\tiny-scenario-runs\baseline examples\tiny-scenario-runs\current --format markdown
```

## Result Shape

A run file can be a single scenario:

```json
{
  "scenario": "menu_startup",
  "status": "passed",
  "duration_ms": 820,
  "assertions": [
    {"name": "main menu visible", "status": "passed"}
  ],
  "artifacts": ["screenshots/menu.png"]
}
```

It can also contain a `scenarios` or `runs` list. Unknown fields are preserved in
the source file and ignored by the report kit.

## Checks

- missing scenario names or statuses;
- failed scenarios and failed assertions;
- missing artifact paths when artifacts are listed;
- new failures compared with a baseline;
- duration regressions compared with a baseline.

## Outputs

- `text`: local terminal report.
- `json`: CI and scripts.
- `markdown`: PR comments and release notes.
- `html`: static artifact for run review.

Reports include the package version, a schema version, and a small rule catalog.
Each finding includes a stable `rule_id` plus a short `rule_help` field so CI
jobs, PR comments, and local scripts can explain what to check next without
hard-coding those messages separately.
