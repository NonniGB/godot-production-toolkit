# Script And CI Usage

Read `tool-manifest.json` first. It declares the CLI entry point, module entry point, output formats, write behavior, and exit-code behavior.

Script-friendly command:

```powershell
godot-signal-audit <project> --autoload EventBus,SignalBus --format json --output signal-report.json --fail-on none
```

Generate a visual architecture graph:

```powershell
godot-signal-audit <project> --format mermaid --output docs/SIGNAL_GRAPH.md --fail-on none
```

Reports may include scene paths, node names, method names, and autoload names. Review before publishing.
