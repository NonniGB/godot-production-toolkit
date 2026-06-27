# Godot Runtime Telemetry Lab

`godot-runtime-telemetry-lab` summarizes and compares lightweight runtime
telemetry from Godot scenario runs, smoke tests, soak tests, or project-owned
debug exporters. It is designed for CI artifacts and release reviews, not as a
replacement for Godot's built-in profiler.

## Install

```powershell
python -m pip install godot-runtime-telemetry-lab
```

From a source checkout:

```powershell
python -m pip install -e .\godot-runtime-telemetry-lab
```

## Quick Start

```powershell
godot-telemetry-lab summarize reports\runtime --format markdown --output reports\runtime.md
godot-telemetry-lab compare reports\baseline reports\current --format json --output reports\runtime-compare.json
godot-telemetry-lab timeline reports\runtime --format html --output reports\runtime-timeline.html
godot-telemetry-lab adapt reports\godot-monitor.csv --format json --output reports\runtime-normalized.json
godot-telemetry-lab adapt godot-runtime-telemetry-lab\examples\tiny-godot-monitor\godot-performance-monitor.csv --format json --output reports\runtime-normalized.json
godot-telemetry-lab budget init --profile android-high --output reports\runtime-budget.json
```

## Input Shape

The tool accepts `.json` or `.csv` files. JSON files can contain a list of
samples, or an object with a `samples`, `frames`, or `events` list.

```json
{
  "samples": [
    {"scenario": "menu", "frame_ms": 12.4, "physics_ms": 2.1, "memory_mb": 180},
    {"scenario": "menu", "frame_ms": 18.8, "physics_ms": 2.5, "memory_mb": 181}
  ]
}
```

Recognized numeric fields are `frame_ms`, `physics_ms`, `memory_mb`, `nodes`,
and `draw_calls`. Timeline output also uses optional `time_s`, `timestamp_s`,
`frame`, `scenario`, `phase`, and `event` fields when they are present.

Use `adapt` when a project-owned Godot exporter writes monitor names such as
`fps`, `Performance.MEMORY_STATIC`, `Performance.OBJECT_NODE_COUNT`, or
`Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME`. The command emits normalized
`samples` that can be fed back into `summarize`, `compare`, or `timeline`.
For official Godot `Performance` monitors, `adapt` treats
`Performance.TIME_PROCESS` and `Performance.TIME_PHYSICS_PROCESS` as seconds
and converts them to milliseconds. Memory monitors such as
`Performance.MEMORY_STATIC`, `Performance.RENDER_VIDEO_MEM_USED`,
`Performance.RENDER_TEXTURE_MEM_USED`, and
`Performance.RENDER_BUFFER_MEM_USED` are treated as bytes and converted to MiB.

## Commands

- `summarize`: reports sample counts, frame percentiles, and budget findings.
- `compare`: compares current telemetry with a baseline and reports frame p95
  and memory max regressions.
- `timeline`: renders a frame and memory timeline as HTML, SVG, Markdown, text,
  or JSON.
- `adapt`: normalizes common Godot monitor and debug-exporter field names.
- `budget init`: writes starter budget JSON for `desktop-dev`, `android-high`,
  `android-low`, or `html5`.

Budget files can be reused with `summarize`, `compare`, and `timeline`:

```powershell
godot-telemetry-lab budget init --profile android-high --output reports\runtime-budget.json
godot-telemetry-lab timeline reports\runtime --budget-file reports\runtime-budget.json --format html --output reports\runtime-timeline.html
```

`compare` includes `frame_p95_delta_ms` and `memory_delta_mb` in JSON reports, so
CI jobs and dashboards can show the size of a runtime change without parsing
the full baseline and current summaries.
JSON reports also include `metadata.rules`, a compact catalog of runtime
telemetry rule titles and help text for scripts, dashboards, and CI comments.

## Outputs

- `text`: local terminal report.
- `json`: CI and scripts.
- `markdown`: PR comments and release notes.
- `html`: self-contained timeline report.
- `svg`: embeddable timeline chart.

## Example

The package includes a tiny runtime fixture:

```powershell
godot-telemetry-lab timeline godot-runtime-telemetry-lab\examples\tiny-runtime-run --format html --output reports\runtime-timeline.html
```

It also includes a tiny Godot monitor CSV fixture:

```powershell
godot-telemetry-lab adapt godot-runtime-telemetry-lab\examples\tiny-godot-monitor\godot-performance-monitor.csv --format json --output reports\runtime-normalized.json
```
