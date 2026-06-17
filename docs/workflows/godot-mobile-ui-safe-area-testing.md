# Godot Mobile UI Safe Area Testing

Use this after exporting UI metadata from Godot menus, HUDs, pause screens, or
touch controls. It checks whether controls fit phone viewports, avoid safe
areas, keep touch targets large enough, and leave enough spacing for real hands.

Related docs: [Tool Index](../TOOL_INDEX.md) and [Use Cases](../USE_CASES.md).

## Packages

- `godot-mobile-ui-doctor` for safe-area, touch-target, spacing, and overlay reports.
- `godot-visual-smoke-test-kit` when viewport plans or screenshots are available.
- `godot-input-map-auditor` when the final readiness report should include input coverage.

## Copy-paste commands

```powershell
python -m pip install godot-mobile-ui-doctor
godot-mobile-ui-doctor mobile-ui.json --format markdown --output reports\mobile-ui.md
godot-mobile-ui-doctor matrix mobile-ui.json --format markdown --output reports\mobile-ui-matrix.md
godot-mobile-ui-doctor overlays mobile-ui.json --output-dir reports\mobile-ui-overlays --fail-on none
```

If the UI is being prepared for localization, set
`thresholds.text_expansion_factor` in `mobile-ui.json` and include the matrix or
readiness report in the same review. When localization stress output exists,
run `layout-risk` to join those strings to exported UI rectangles:

```powershell
godot-mobile-ui-doctor layout-risk mobile-ui.json --stress-pack reports\localization-stress\stress-pack-manifest.json --format markdown --output reports\mobile-layout-risk.md
```

Reuse viewport data from a visual smoke plan when available:

```powershell
godot-visual-smoke plan visual-smoke.toml --project . --format json --output reports\visual-plan.json
godot-mobile-ui-doctor readiness mobile-ui.json --visual-smoke-plan reports\visual-plan.json --format markdown --output reports\mobile-readiness.md
```

## Expected inputs

- `mobile-ui.json` with resolved `Control` rectangles, labels, viewports, and safe areas.
- Optional screenshots for overlay output.
- Optional input, export, mobile performance, localization, or visual smoke reports.

## Expected outputs

- Markdown or JSON findings for touch targets, spacing, safe areas, and overflow risk.
- Optional PNG overlays in `reports\mobile-ui-overlays`.
- A readiness report that combines UI findings with other mobile checks.
