# Mobile UI Metadata

The tool expects layout rectangles after Godot has resolved anchors,
containers, scaling, and text sizes. This makes the checks independent of any
particular scene structure.

Each screen points at a named viewport. Each node contains:

- `id`: stable id used in reports;
- `kind`: optional UI type such as `button`, `label`, or `panel`;
- `x`, `y`, `width`, `height`: viewport-pixel rectangle;
- `text`: visible label text when relevant;
- `font_size`: estimated rendered font size;
- `interactive`: true for buttons, sliders, touch zones, tabs, list rows, or menu items.

The exported metadata should avoid secrets and avoid unnecessary private content.
For many projects, stable technical ids are enough.

Optional `thresholds.text_expansion_factor` enables localized-label layout risk
checks. Values above `1.0` multiply the estimated text width before comparing it
with the node rectangle; for example, `1.4` checks a 40% expansion.

This expansion factor is a useful first pass when the metadata contains only
current source text. For tighter UI review, generate localization stress
catalogs with `godot-l10n-guard stress-pack`, load those strings in a
project-owned capture step, and export metadata from the stressed screens.

Viewport definitions can also come from `godot-visual-smoke plan --format json`
by passing `--visual-smoke-plan`. In that workflow, `mobile-ui.json` can focus on
screens and nodes while the visual smoke config owns shared phone and tablet
viewport sizes.
