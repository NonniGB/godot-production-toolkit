# Godot Visual Regression Testing

Use this for menus, HUDs, settings screens, inventory screens, title screens, or
other stable Godot views where screenshots should not change unexpectedly. It
works best when the project already has a scripted way to capture the same
screens at the same viewport sizes.

Related docs: [Tool Index](../TOOL_INDEX.md) and [Use Cases](../USE_CASES.md).

## Packages

- `godot-visual-smoke-test-kit` for capture planning, screenshot comparison, and baseline approval.
- `godot-mobile-ui-doctor` when screenshot viewports should also drive mobile UI checks.

## Copy-paste commands

```powershell
python -m pip install godot-visual-smoke-test-kit
godot-visual-smoke plan visual-smoke.toml --project . --format json --output reports\visual-plan.json
godot-visual-smoke compare baselines\main-menu.png screenshots\main-menu.png --diff reports\visual-diffs\main-menu.png --format json --output reports\visual-main-menu.json
```

Approve a deliberate screenshot update:

```powershell
godot-visual-smoke approve screenshots\main-menu.png baselines\main-menu.png
```

## Expected inputs

- A `visual-smoke.toml` capture plan, or direct baseline and current PNG paths.
- Baseline screenshots committed or stored by the project.
- Current screenshots produced by a local or CI capture step.

## Expected outputs

- JSON or text comparison reports.
- PNG diff images for changed screenshots.
- Updated baselines only when `approve` is run deliberately.

