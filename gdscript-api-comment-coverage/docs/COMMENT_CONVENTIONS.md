# Comment Conventions

Use a short comment immediately above public APIs:

```gdscript
## Emitted when the selection changes.
signal selection_changed(id: String)

## Applies a selected item.
func apply_selection(id: String) -> void:
    pass
```

The scanner accepts `##` and `#` comments. `##` is recommended because it matches Godot's built-in documentation style.

Blank lines break the association between a comment and the API below it.
