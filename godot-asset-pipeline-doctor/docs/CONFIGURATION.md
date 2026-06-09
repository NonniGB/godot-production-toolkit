# Configuration

The CLI accepts explicit flags and can also read TOML configuration.

Default config path:

```text
.godot-asset-doctor.toml
```

Example:

```toml
profile = "pixel-2d"
format = "json"
fail_on = "warning"
output = "asset-report.json"
exclude = ["addons/vendor/**", "assets/generated/**"]
max_texture_dimension = 4096
large_texture_mb = 16
max_palette_colors = 256
large_audio_mb = 8
max_audio_duration_seconds = 120
```

Run with the default project-local config:

```powershell
godot-asset-doctor C:\Projects\ArcadePrototype
```

Run with an explicit config:

```powershell
godot-asset-doctor C:\Projects\ArcadePrototype --config C:\Projects\ArcadePrototype\ci-asset-checks.toml
```

CLI flags override config values.

## Fields

### `profile`

Allowed values:

- `default`
- `pixel-2d`
- `android-mobile`
- `audio-mobile`

### `format`

Allowed values:

- `text`
- `json`

### `fail_on`

Allowed values:

- `none`
- `warning`
- `error`

Use `warning` for strict CI gates and `error` for lower-noise release checks.

### `output`

Optional path for writing the report.

### `exclude`

Optional list of project-relative glob patterns. Use this for generated assets, third-party addons, exported screenshots, or any folder that should not be part of the asset quality gate.

```toml
exclude = [
  "addons/vendor/**",
  "assets/generated/**",
]
```

### `max_texture_dimension`

Maximum allowed PNG width or height before `texture_dimension_too_large` is reported. The default is `4096`.

Raise this only when your target platforms are known to support larger textures. Lower it for strict mobile or low-memory projects.

### `large_texture_mb`

Estimated RGBA memory threshold, in MiB, before `texture_memory_large` is reported. The default is `16`.

This is based on uncompressed RGBA memory, not source PNG file size.

### `max_palette_colors`

Maximum unique RGBA color count before `large_palette` is reported in pixel-art profiles. The default is `256`.

Lower this for tight sprite palettes, or raise it for painted UI and background art that still lives in the same asset tree.

### `large_audio_mb`

Source audio file-size threshold, in MiB, before `audio_file_large` is reported. The default is `8`.

Lower this for strict mobile/web builds. Raise it for projects that intentionally ship longer music or narration.

### `max_audio_duration_seconds`

WAV duration threshold before `audio_duration_long` is reported. The default is `120`.

This check only reports duration when the tool can read the WAV header. OGG and MP3 files still receive file-size and import-metadata checks.

## Default Ignored Folders

The scanner skips common non-asset or generated folders by default:

- `.git`
- `.godot`
- `.playwright-cli`
- `.venv`
- `__pycache__`
- `build`
- `dist`
- `docs`
- `logs`
- `node_modules`
- `test-results`
- `venv`
