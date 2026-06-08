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

[[scenes]]
name = "menu_portrait"
path = "res://scenes/menu.tscn"
viewport = "portrait_phone"
```

Use stable scene names because they become screenshot filenames.
