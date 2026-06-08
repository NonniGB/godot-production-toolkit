# Script And CI Usage

Read `tool-manifest.json` first. It declares the CLI entry point, module entry point, output formats, write behavior, and exit-code behavior.

Script-friendly validation command:

```powershell
godot-save-guard validate <fixtures> --schema <schema.json> --format json --output save-report.json --fail-on none
```

The `migrate` command executes a user-supplied command template. Use validation mode unless you intentionally want to run migrations.

Reports can include save fixture paths and schema fields. Avoid publishing real player saves or private fixtures.
