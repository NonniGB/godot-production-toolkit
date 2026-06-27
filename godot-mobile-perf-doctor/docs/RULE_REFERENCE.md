# Rule Reference

- `forward_plus_renderer_mobile_risk`: Forward+ can be expensive for many mobile 2D projects and should be tested carefully on target devices.
- `large_base_viewport`: base viewport exceeds the active profile or configured pixel budget.
- `stretch_disabled`: stretch mode is disabled or missing, which can make mobile scaling unpredictable.
- `stretch_aspect_ignore`: stretch aspect ignores the viewport shape, which can distort phone layouts.
- `missing_mobile_ui_metadata`: configured mobile UI metadata was not found, so safe-area and touch-layout evidence is missing.
- `large_texture_dimension`: PNG dimension exceeds the active profile or configured maximum.
- `missing_project_godot`: project settings could not be audited because the scan root does not contain a Godot project file.
