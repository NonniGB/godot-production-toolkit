# Agentic Usage

Read `agent-tool.json` first. It declares the CLI entry point, module entry point, output formats, write behavior, and exit-code contract.

Agent-safe command:

```powershell
godot-signal-audit <project> --autoload EventBus,SignalBus --format json --output signal-report.json --fail-on none
```

Generate a visual architecture graph:

```powershell
godot-signal-audit <project> --format mermaid --output docs/SIGNAL_GRAPH.md --fail-on none
```

Reports may include scene paths, node names, method names, and autoload names. Review before publishing.
