# Godot Scenario Report Kit

`godot-scenario-report-kit` validates and summarizes scenario run evidence from
Godot projects. It reads the kit's small JSON result shape and common JUnit XML
from GUT, GdUnit4, or custom runners. It does not replace those runners; it
helps compare their output in CI and review artifacts.

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

Summarize JUnit XML from an existing test runner:

```powershell
godot-scenario-report summarize examples\tiny-scenario-runs\junit.xml --format markdown
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

Group retries from a runner that records multiple attempts in one result file
or folder:

```powershell
godot-scenario-report flake compare examples\tiny-scenario-runs\retry-run --format markdown
```

Bundle scenario evidence with nearby telemetry and visual reports:

```powershell
godot-telemetry-lab timeline reports\runtime --format json --output reports\runtime-timeline.json
godot-scenario-report bundle examples\tiny-scenario-runs\current --manifest examples\tiny-scenario-runs\scenario-manifest.json --telemetry reports\runtime-timeline.json --visual examples\tiny-scenario-runs\visual-smoke.json --evidence log=examples\tiny-scenario-runs\run.log --evidence junit=examples\tiny-scenario-runs\junit.xml --format json --output reports\scenario-bundle.json
```

## Result Shape

A run file can be a single JSON scenario:

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

JUnit XML is also accepted wherever a result file or result directory is used.
Each `<testcase>` becomes one scenario. `classname` and `name` are joined into a
stable scenario id, `time` is converted from seconds to milliseconds, and
`<failure>` or `<error>` children become failed assertions. `<skipped>` children
produce skipped scenarios.

## Checks

- missing scenario names or statuses;
- failed scenarios and failed assertions;
- unreadable JUnit XML files;
- missing artifact paths when artifacts are listed;
- new failures compared with a baseline;
- duration regressions compared with a baseline.
- manifest entries without results, owners, tags, or expected artifacts;
- missing required tag, platform, or critical-flow coverage;
- scenarios whose status changes across repeated runs;
- retried scenarios, including attempt count, ordered statuses, and final
  status.
- missing artifacts or linked evidence paths in a bundle report, including
  telemetry, visual smoke, logs, JUnit XML, profiler captures, or other review
  files.

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

When `--telemetry` points at JSON from `godot-runtime-telemetry-lab`, the bundle
adds a compact `telemetry_summary` with sample count, frame p95, frame max,
memory max, spike count, and finding counts. Raw telemetry samples are not
copied into the bundle.

When `--visual` points at JSON from a visual smoke or screenshot comparison
tool, the bundle adds a compact `visual_summary` with capture count, comparison
count, changed comparisons, warnings, and errors. The bundle links screenshots
or diff reports by path; it does not copy or embed images.

Use `--evidence KIND=PATH` for extra files that help a human review the run,
such as `log=reports\run.log`, `junit=reports\junit.xml`, or
`profile=reports\frame-profile.html`. The bundle links these files; it does not
copy, rewrite, or inline them. Keep paths relative to the review artifact folder
when possible, and check that logs or reports do not include private machine
paths before sharing them.

Reports include the package version, a schema version, and a small rule catalog.
Each finding includes a stable `rule_id` plus a short `rule_help` field so CI
jobs, PR comments, and local scripts can explain what to check next without
hard-coding those messages separately.
