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
