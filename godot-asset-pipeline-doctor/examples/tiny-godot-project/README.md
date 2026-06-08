# Tiny Godot Project Example

This is a minimal generic project layout for trying the CLI.

Run from this repository root:

```powershell
python -m godot_asset_doctor examples\tiny-godot-project --profile pixel-2d --fail-on none
```

Expected result: one `transparent_edge_rgb` warning for `assets/sample_sprite.png`. The image is a tiny generated placeholder that intentionally includes hidden RGB data under one transparent edge pixel.

The example intentionally uses placeholder names. When adapting it for a private project, keep project-specific data out of public bug reports and documentation snippets.
