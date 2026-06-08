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
godot-signal-audit . --format mermaid --output docs\SIGNAL_GRAPH.md
godot-signal-audit . --format json --output signal-report.json
```

Run the sample:

```powershell
godot-signal-audit examples\tiny-godot-project --format mermaid --fail-on none
```

## What It Checks

- Persistent scene connections in `.tscn` files.
- Target method existence when the target script is resolvable.
- GDScript `signal` declarations and method names.
- Configured autoload signal connect usage.
- Mermaid signal graph output.

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
