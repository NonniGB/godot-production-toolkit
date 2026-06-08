# Agentic Usage

Read `agent-tool.json` first. It declares the CLI entry point, module entry point, output formats, write behavior, and exit-code contract.

Agent-safe command:

```powershell
godot-mobile-perf-doctor <project> --static --format json --output mobile-perf-report.json --fail-on none
```

Human release report:

```powershell
godot-mobile-perf-doctor <project> --static --format markdown --output mobile-perf-report.md
```

Reports may include local asset paths and device names if `--adb-summary` is used.
