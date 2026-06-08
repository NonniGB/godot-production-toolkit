# Pixel-Art Workflow

Use the `pixel-2d` profile for sprite folders, UI icons, tiles, and other assets where crisp edges matter.

```powershell
godot-asset-doctor . --profile pixel-2d --fail-on warning
```

The profile focuses on:

- mipmaps on pixel-art assets
- alpha-border fixing on transparent assets
- transparent RGB contamination on sprite edges
- unexpectedly large color palettes
- missing `.import` metadata

## Transparent RGB Contamination

A PNG pixel can be fully transparent while still carrying hidden RGB values. Those values can bleed into visible pixels when filtering, resizing, or texture bleeding occurs. The checker reports contamination on the image edge because that is where fringe artifacts commonly appear.

## Keeping Public Examples Generic

Examples should use tiny placeholder sprites, UI buttons, icons, or tiles. Do not publish private game project data, production asset paths, or unreleased design-specific naming.

