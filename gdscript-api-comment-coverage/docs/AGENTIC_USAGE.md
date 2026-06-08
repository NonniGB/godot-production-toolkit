# Agentic Usage

Read `agent-tool.json` first. It declares the CLI entry point, module entry point, output formats, write behavior, and exit-code contract.

Agent-safe command:

```powershell
gdscript-api-coverage <project> --format json --output gdscript-api-report.json --fail-on none
```

Generate human docs separately:

```powershell
gdscript-api-coverage <project> --write-docs docs/API_INDEX.md --min-all 80
```

Generated reports include script paths, class names, signal names, and method names. Avoid publishing reports from private projects without review.
