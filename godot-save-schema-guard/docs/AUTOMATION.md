# Script And CI Usage

Read `tool-manifest.json` first. It declares the CLI entry point, module entry point, output formats, write behavior, and exit-code behavior.

Script-friendly validation command:

```powershell
godot-save-guard validate <fixtures> --schema <schema.json> --format json --output save-report.json --fail-on none
```

The `migrate` command executes a user-supplied command template. Use validation mode unless you intentionally want to run migrations.

Before sharing fixtures outside your project, create reviewed sanitized copies:

```powershell
godot-save-guard redact <fixtures> --path player.name --path players.*.email --output-dir sanitized-fixtures --dry-run --format markdown
godot-save-guard redact <fixtures> --path player.name --path players.*.email --output-dir sanitized-fixtures --format json --output redaction-report.json
```

Reports can include save fixture paths and schema fields. Avoid publishing real
player saves or private fixtures. Redaction only changes the paths you list, so
review sanitized output before sharing it.
