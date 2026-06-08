# Generated Output

Write Markdown reference docs:

```powershell
godot-input-audit . --write-docs docs\INPUT_REFERENCE.md
```

Write GDScript constants:

```powershell
godot-input-audit . --generate-gd scripts\generated\input_actions.gd
```

Generated constants look like:

```gdscript
class_name InputActions

const MOVE_LEFT = "move_left"
```
