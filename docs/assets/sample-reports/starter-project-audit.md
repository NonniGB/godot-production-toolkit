# Starter Project Audit Sample

This is a short, synthetic example based on
`examples/release-readiness-demo`. It shows the kind of first-pass output a new
Godot project can produce before a full CI setup exists.

| Tool | Errors | Warnings | What It Found |
|---|---:|---:|---|
| `godot-asset-pipeline-doctor` | 0 | 3 | Pixel-art texture import settings that may blur or fringe UI art. |
| `godot-export-preset-doctor` | 4 | 2 | Android export preset fields that need package, version, ABI, icon, and debug review. |
| `godot-input-map-auditor` | 3 | 0 | Input actions missing touch coverage for a mobile-facing project. |
| `godot-mobile-perf-doctor` | 0 | 3 | Renderer, viewport, and stretch settings that need an explicit mobile decision. |

## Useful Next Steps

- Fix package identity, version, ABI, and export path fields before a real Android build.
- Add touch bindings or document why an action is keyboard/controller only.
- Revisit texture import flags for pixel UI assets.
- Pick a renderer, base viewport, and stretch mode deliberately instead of inheriting defaults.

## Related Reports

- [Project doctor summary](release-readiness-summary.md)
- [Asset report](assets.json)
- [Export report](export.json)
- [Input map report](input-map.json)
- [Mobile performance report](mobile-perf.json)
- [Dashboard sample](release-dashboard-demo.html)
