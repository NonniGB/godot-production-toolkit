# Godot Scene Signal Auditor

Static CI checks for Godot scene signal connections, signal declarations, autoload signal usage, and coupling patterns that become hard to debug in larger projects.

The analyzer is deliberately conservative. It reports only what it can infer from `.tscn` and `.gd` files without running Godot.

## Install

```powershell
python -m pip install -e .
```

When published:

```powershell
python -m pip install godot-scene-signal-auditor
```

## Quick Start

```powershell
godot-signal-audit C:\Projects\MyGame --strict-stale-connections
godot-signal-audit . --autoload EventBus,SignalBus
godot-signal-audit . --contract scene-contract.json
godot-signal-audit . --format mermaid --output docs\SIGNAL_GRAPH.md
godot-signal-audit . --format json --output signal-report.json
```

Run the sample:

```powershell
godot-signal-audit examples\tiny-godot-project --format mermaid --fail-on none
godot-signal-audit examples\tiny-godot-project --contract examples\tiny-godot-project\scene-contract.json --format json
```

## What It Checks

- Persistent scene connections in `.tscn` files.
- Target method existence when the target script is resolvable.
- GDScript `signal` declarations and method names.
- Configured autoload signal connect usage.
- Optional JSON or TOML scene contracts for required nodes, connections, script methods, and script signals.
- Mermaid signal graph output.
- Report metadata and readable rule explanations in text and JSON output.

## Scene Contracts

Use `--contract` to enforce a small scene API before refactors. Contracts can target exact scene paths or glob-style `path_pattern` values.

```json
{
  "scenes": [
    {
      "path": "scenes/menu.tscn",
      "required_nodes": [".", "StartButton"],
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
        ".": ["menu_opened"]
      }
    }
  ]
}
```

TOML files use the same field names with `[[scenes]]` entries. Contract violations are reported as errors and respect `--fail-on`.

## Documentation

- [Rule reference](docs/RULE_REFERENCE.md)
- [Mermaid graphs](docs/MERMAID.md)
- [Autoload usage](docs/AUTOLOADS.md)
- [Limitations](docs/LIMITATIONS.md)
- [CI usage](docs/CI.md)

## Development

```powershell
python -m pip install -e .
python -m unittest discover -s tests -v
godot-signal-audit examples\tiny-godot-project --format mermaid --fail-on none
```

Examples use generic scene and signal names so the repository can be published safely.
