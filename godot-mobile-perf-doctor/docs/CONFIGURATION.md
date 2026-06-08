# Configuration

Create `.godot-mobile-perf-doctor.toml` in the Godot project root:

```toml
profile = "portrait-2d"
format = "markdown"
fail_on = "warning"
output = "reports/mobile-perf.md"
max_texture_dimension = 2048
max_viewport_pixels = 2073600
adb_summary = "reports/adb-summary.txt"
```

CLI flags override config values:

```powershell
godot-mobile-perf-doctor C:\Projects\ArcadePrototype --static --format json
```

## Fields

- `profile`: currently `portrait-2d`.
- `format`: `text`, `json`, `markdown`, or `sarif`.
- `fail_on`: `warning`, `error`, or `none`.
- `output`: optional report file path.
- `max_texture_dimension`: PNG width or height threshold for `large_texture_dimension`.
- `max_viewport_pixels`: base viewport pixel budget for `large_base_viewport`.
- `adb_summary`: optional path to captured adb summary text.

For a strict 720p mobile budget, use:

```toml
max_viewport_pixels = 921600
```

For a more relaxed 1080p budget, use the default:

```toml
max_viewport_pixels = 2073600
```
