# Rule Reference

Godot Asset Pipeline Doctor emits issues with three severities:

- `error`: likely to break compatibility or exceed a conservative engine/device limit.
- `warning`: likely to cause visual quality, memory, or release-readiness problems.
- `info`: reserved for future non-blocking notes.

## Common Rules

### `missing_import_metadata`

Severity: `warning`

The PNG has no adjacent Godot `.import` file. This usually means the asset has not been imported by Godot yet, or the generated metadata is not committed.

Suggestion: open the project in Godot and reimport assets before relying on import-setting checks.

### `texture_dimension_too_large`

Severity: `error`

One axis exceeds 4096 pixels. Some target devices may support larger textures, but this is risky for portable releases.

Suggestion: split or downscale the texture, or verify the real target-device limit.

## Pixel 2D Rules

### `large_palette`

Severity: `warning`

The image has more than 256 unique RGBA colors. This may be intentional, but it often indicates blended or anti-aliased art in a pixel-art asset folder.

### `pixel_mipmaps_enabled`

Severity: `warning`

Mipmaps are enabled for a pixel-art profile asset. This can soften crisp art when scaled.

### `alpha_border_fix_disabled`

Severity: `warning`

The image has transparency, but Godot alpha-border fixing is disabled.

### `transparent_edge_rgb`

Severity: `warning`

Fully transparent edge pixels contain non-black RGB values. These hidden colors can bleed into visible edges depending on filtering and import settings.

## Android Mobile Rules

### `texture_memory_large`

Severity: `warning`

The texture would occupy at least 16 MiB as RGBA in memory.

Suggestion: reduce dimensions, review compression/import settings, or split the asset by use case.

