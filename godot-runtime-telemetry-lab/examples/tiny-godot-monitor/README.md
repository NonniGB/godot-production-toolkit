# Tiny Godot Monitor Export

This fixture shows the shape of a small CSV produced by a project-owned Godot
script that calls `Performance.get_monitor(...)` during a smoke or scenario run.

Godot `Performance.TIME_PROCESS` and `Performance.TIME_PHYSICS_PROCESS` values
are seconds, while render memory monitor values are bytes. `adapt` normalizes
those fields into toolkit-friendly milliseconds and MiB. The adapter accepts
wide rows with one column per monitor, or long rows with `monitor` and `value`
columns.

```powershell
godot-telemetry-lab adapt godot-runtime-telemetry-lab\examples\tiny-godot-monitor\godot-performance-monitor.csv --format json --output reports\runtime-normalized.json
godot-telemetry-lab adapt godot-runtime-telemetry-lab\examples\tiny-godot-monitor\godot-performance-monitor-long.csv --format json --output reports\runtime-normalized-long.json
godot-telemetry-lab timeline reports\runtime-normalized.json --budget-profile android-high --format html --output reports\runtime-timeline.html
```
