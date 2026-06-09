# Configuration

`visual-smoke.toml`:

```toml
[settings]
pixel_tolerance = 2
max_changed_percent = 0.1
output_dir = "visual-smoke-output"

[viewports.portrait_phone]
width = 720
height = 1280
safe_area = { top = 48, bottom = 24 }

[[scenes]]
name = "menu_portrait"
path = "res://scenes/menu.tscn"
viewport = "portrait_phone"
```

Use stable scene names because they become screenshot filenames.

## Viewport Manifests

Put shared viewport definitions in a separate file when several configs need the
same device classes:

```toml
# viewports.toml
[viewports.portrait_phone]
width = 720
height = 1280
safe_area = { top = 48, bottom = 24 }

[viewports.tablet]
width = 1536
height = 2048
safe_area = { left = 12, right = 12 }
```

Reference it from `visual-smoke.toml`:

```toml
[settings]
viewport_manifest = "viewports.toml"
```

Or pass it on the command line:

```powershell
godot-visual-smoke plan visual-smoke.toml --project . --viewport-manifest viewports.toml --format json
```

Inline viewport definitions override manifest entries with the same name. The
planned JSON output includes `safe_area` so other tools can combine screenshot
evidence with mobile UI checks.
