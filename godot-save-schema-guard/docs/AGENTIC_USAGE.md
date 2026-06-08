# Agentic Usage

Read `agent-tool.json` first. It declares the CLI entry point, module entry point, output formats, write behavior, and exit-code contract.

Agent-safe validation command:

```powershell
godot-save-guard validate <fixtures> --schema <schema.json> --format json --output save-report.json --fail-on none
```

The `migrate` command executes a user-supplied command template. Agents should prefer validation mode unless the user explicitly asks to run migrations.

Reports can include save fixture paths and schema fields. Avoid publishing real player saves or private fixtures.
