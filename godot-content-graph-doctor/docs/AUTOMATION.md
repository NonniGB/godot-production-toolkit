# Automation

Configured collections are required inputs. Missing, unreadable, malformed, or
unsupported collection files produce error findings; automation should not
interpret an empty collection count as proof that the source loaded correctly.

Use JSON output for CI:

```powershell
godot-content-graph . --config content-graph.toml --format json --output reports\content-graph.json --fail-on error
```

Use Markdown output for a human-readable artifact:

```powershell
godot-content-graph . --config content-graph.toml --format markdown --output reports\content-graph.md --fail-on none
```

The command is deterministic and does not access the network.
