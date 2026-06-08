# Agentic Usage

Read `agent-tool.json` first. It declares the CLI entry point, module entry point, output formats, write behavior, and exit-code contract.

Agent-safe command:

```powershell
godot-l10n-guard <project> --translations translations --scan-scripts --scan-scenes --format json --output localization-report.json --fail-on none
```

Use Markdown for release QA:

```powershell
godot-l10n-guard <project> --translations translations --require fr,es,de --format markdown --output docs/LOCALIZATION_QA.md
```

Reports may contain source strings and localization keys. Review before publishing from private projects.
