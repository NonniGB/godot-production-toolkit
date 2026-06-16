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
and `draw_calls`. Unknown fields are ignored by the first release.

## Commands

- `summarize`: reports sample counts, frame percentiles, and budget findings.
- `compare`: compares current telemetry with a baseline and reports regressions.

## Outputs

- `text`: local terminal report.
- `json`: CI and scripts.
- `markdown`: PR comments and release notes.
