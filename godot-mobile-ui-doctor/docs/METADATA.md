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

Viewport definitions can also come from `godot-visual-smoke plan --format json`
by passing `--visual-smoke-plan`. In that workflow, `mobile-ui.json` can focus on
screens and nodes while the visual smoke config owns shared phone and tablet
viewport sizes.
