# Godot Runtime Performance Regression

Use this after scenario runs, soak tests, device captures, or custom telemetry
exports produce frame timing and runtime samples. It helps compare current runs
against a baseline and turn raw Godot performance data into a report that can be
read in CI.

Related docs: [Tool Index](../TOOL_INDEX.md) and [Use Cases](../USE_CASES.md).

## Packages

- `godot-runtime-telemetry-lab` for budgets, summaries, baseline comparison, and timelines.
- `godot-scenario-report-kit` when performance samples are tied to scenario runs.

## Copy-paste commands

```powershell
python -m pip install godot-runtime-telemetry-lab
godot-telemetry-lab budget init --profile android-high --output reports\runtime-budget.json
godot-telemetry-lab summarize reports\runtime --budget-file reports\runtime-budget.json --format markdown --output reports\runtime-summary.md
godot-telemetry-lab compare reports\baseline-runtime reports\current-runtime --budget-file reports\runtime-budget.json --format markdown --output reports\runtime-compare.md
godot-telemetry-lab timeline reports\current-runtime --budget-file reports\runtime-budget.json --format html --output reports\runtime-timeline.html
```

If your Godot runner writes monitor-style CSV or JSON fields, normalize them
first:

```powershell
godot-telemetry-lab adapt reports\godot-monitor.csv --format json --output reports\runtime-normalized.json
godot-telemetry-lab timeline reports\runtime-normalized.json --budget-file reports\runtime-budget.json --format html --output reports\runtime-timeline.html
```

Godot `Performance.TIME_PROCESS` and `Performance.TIME_PHYSICS_PROCESS` values
are seconds. The adapter converts them to milliseconds, and converts Godot
memory monitor byte counters to MiB, before writing normalized samples.

## Expected inputs

- Runtime telemetry in JSON or CSV.
- Common fields such as `frame_ms`, `physics_ms`, `memory_mb`, `nodes`, `draw_calls`, `scenario`, `phase`, and `time_s`.
- Optional Godot monitor fields such as `fps`, `Performance.TIME_PROCESS`,
  `Performance.TIME_PHYSICS_PROCESS`, `Performance.MEMORY_STATIC`,
  `Performance.RENDER_VIDEO_MEM_USED`, `Performance.OBJECT_NODE_COUNT`, and
  `Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME`.
- Optional baseline and current telemetry folders.
- Optional budget JSON created by `budget init`.

## Expected outputs

- Markdown, JSON, text, HTML, or SVG reports.
- Baseline comparison findings for frame time, memory, or other tracked metrics.
- Timeline artifacts that help explain spikes by scenario phase.
