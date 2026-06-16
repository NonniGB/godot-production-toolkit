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

Check a scenario manifest and coverage policy:

```powershell
godot-scenario-report manifest check examples\tiny-scenario-runs\scenario-manifest.json --results examples\tiny-scenario-runs\current --format markdown
godot-scenario-report manifest coverage examples\tiny-scenario-runs\scenario-manifest.json --results examples\tiny-scenario-runs\current --format html --output reports\scenario-coverage.html
```

Compare repeated runs for flaky status changes:

```powershell
godot-scenario-report flake compare examples\tiny-scenario-runs\baseline examples\tiny-scenario-runs\current examples\tiny-scenario-runs\repeat-run --format markdown
```

Bundle scenario evidence with nearby telemetry and visual reports:

```powershell
godot-scenario-report bundle reports\scenarios --manifest scenario-manifest.json --telemetry reports\runtime-timeline.html --visual reports\visual-smoke.json --format json --output reports\scenario-bundle.json
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
- manifest entries without results, owners, tags, or expected artifacts;
- missing required tag, platform, or critical-flow coverage;
- scenarios whose status changes across repeated runs.
- missing artifacts or linked telemetry/visual evidence in a bundle report.

## Manifest Shape

Scenario manifests are optional. They help teams describe the suite they expect
to run, rather than only summarizing whatever files happened to be written:

```json
{
  "coverage": {
    "required_tags": ["smoke", "economy"],
    "required_critical_flows": ["startup", "trade"],
    "required_platforms": ["desktop", "android"]
  },
  "scenarios": [
    {
      "id": "menu_startup",
      "owner": "ui",
      "tags": ["smoke"],
      "critical_flows": ["startup"],
      "platforms": ["desktop"],
      "expected_artifacts": ["screenshots/menu.png"]
    }
  ]
}
```

## Outputs

- `text`: local terminal report.
- `json`: CI and scripts.
- `markdown`: PR comments and release notes.
- `html`: static artifact for run review.

The `bundle` command is intended for release dashboards and PR artifacts. It
does not rewrite project-owned evidence; it builds a compact manifest of
scenario results, listed artifacts, and optional telemetry or visual-smoke
reports so reviewers can see which files belong together.

Reports include the package version, a schema version, and a small rule catalog.
Each finding includes a stable `rule_id` plus a short `rule_help` field so CI
jobs, PR comments, and local scripts can explain what to check next without
hard-coding those messages separately.
