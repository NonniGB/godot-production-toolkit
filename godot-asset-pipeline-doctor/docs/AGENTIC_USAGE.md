# Agentic Usage

Read `agent-tool.json` first. It declares the CLI entry point, module entry point, output formats, write behavior, and exit-code contract.

Agent-safe command:

```powershell
godot-asset-doctor <project> --profile android-mobile --format json --output asset-report.json --fail-on none
```

Use `--fail-on none` when collecting evidence so the command returns `0` even when findings are present. Use `--fail-on warning` or `--fail-on error` for CI gates.

The tool does not execute project code, does not require network access, and writes only when `--output` is provided.
