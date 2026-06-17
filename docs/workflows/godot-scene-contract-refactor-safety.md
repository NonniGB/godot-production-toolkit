# Godot Scene Contract Refactor Safety

Use this before renaming nodes, moving UI scenes, splitting controllers, or
changing signal handlers. A small scene contract gives reviewers a concrete
check that important scene API points still exist after the refactor.

Related docs: [Tool Index](../TOOL_INDEX.md) and [Workflow Finder](../search-index.md).

## Packages

- `godot-scene-signal-auditor` for `.tscn` signal wiring and scene contracts.
- `godot-gdscript-architecture-guard` when the same refactor changes module or
  autoload boundaries.

## Copy-paste commands

```powershell
python -m pip install godot-scene-signal-auditor godot-gdscript-architecture-guard
godot-signal-audit . --contract scene-contract.json --format json --output reports\scene-contract.json
godot-architecture-guard . --config architecture-guard.toml --format markdown --output reports\architecture.md
```

## Minimal contract

```json
{
  "scenes": [
    {
      "path": "scenes/main_menu.tscn",
      "required_nodes": [".", "StartButton", "OptionsButton"],
      "required_connections": [
        {
          "from": "StartButton",
          "signal": "pressed",
          "to": ".",
          "method": "_on_start_pressed"
        }
      ],
      "script_methods": {
        ".": ["_ready", "_on_start_pressed"]
      },
      "script_signals": {
        ".": ["menu_confirmed"]
      }
    }
  ]
}
```

Use exact `path` values for important scenes and `path_pattern` values such as
`ui/**/*.tscn` for broader conventions.

## Expected inputs

- Godot `.tscn` files.
- GDScript files referenced by those scenes.
- Optional JSON or TOML scene contract file.
- Optional architecture guard config for module boundary checks.

## Expected outputs

- JSON, text, or Mermaid signal reports.
- Contract violations for missing nodes, connections, methods, or script
  signals.
- Architecture findings when the refactor crosses module or autoload rules.
- Module ownership summaries showing which areas own scripts, incoming/outgoing
  dependencies, autoload references, hotspots, and possible-unused candidates.
