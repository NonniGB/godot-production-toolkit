# Mermaid Graphs

Generate a Mermaid graph:

```powershell
godot-signal-audit . --format mermaid --output docs\SIGNAL_GRAPH.md
```

Example:

```mermaid
flowchart LR
  "StartButton" -->|"pressed / _on_start_pressed"| "."
```

The graph is intentionally simple and focuses on persistent scene connections.
