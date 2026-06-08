# Static Checks

The first release checks:

- `rendering/renderer/rendering_method`
- `display/window/size/viewport_width`
- `display/window/size/viewport_height`
- `display/window/stretch/mode`
- PNG texture dimensions and estimated RGBA memory

Static checks are fast and CI-friendly, but they do not replace device testing.

The viewport and texture thresholds can be tuned in `.godot-mobile-perf-doctor.toml` or with CLI flags. This lets a small portrait game use stricter budgets than a tablet-focused project.
