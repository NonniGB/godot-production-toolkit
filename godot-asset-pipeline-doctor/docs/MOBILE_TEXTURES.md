# Mobile Texture Guide

Use the `android-mobile` profile for release checks targeting Android or other memory-constrained devices.

```powershell
godot-asset-doctor . --profile android-mobile --format text
```

The first release estimates memory using uncompressed RGBA size:

```text
width * height * 4 bytes
```

This is intentionally conservative. Runtime memory depends on compression, import settings, atlas strategy, renderer, and device support.

## Practical Checks

- Review every texture at or above 16 MiB estimated RGBA memory.
- Avoid very large single backgrounds when layered smaller assets would work.
- Keep UI and sprite atlases scoped by scene or feature instead of building one huge atlas.
- Re-run the scan before Android export.

