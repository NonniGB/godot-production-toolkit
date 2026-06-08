# Static Checks

The first release checks:

- `rendering/renderer/rendering_method`
- `display/window/size/viewport_width`
- `display/window/size/viewport_height`
- `display/window/stretch/mode`
- PNG texture dimensions and estimated RGBA memory

Static checks are fast and CI-friendly, but they do not replace device testing.
