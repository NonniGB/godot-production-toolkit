# Rule Reference

- `missing_project_godot`: no project file was found.
- `input_map_empty`: no `[input]` actions were found.
- `action_has_no_events`: an action exists but has no bound events.
- `missing_required_device`: an action does not have every device family requested by `--require` or by its policy group.
- `duplicate_binding`: the same normalized event signature is assigned to more than one action.

Duplicate bindings are warnings because some projects intentionally map UI and gameplay actions to the same physical input. Required-device failures are errors because they usually block a target platform.
