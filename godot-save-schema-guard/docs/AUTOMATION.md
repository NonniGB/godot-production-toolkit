# Script And CI Usage

Migration commands run without a system shell and have a 120-second timeout by
default. Use `--timeout` when a reviewed migration needs longer. Nested fixture
paths are preserved under the output directory to prevent filename collisions.

Read `tool-manifest.json` first. It declares the CLI entry point, module entry point, output formats, write behavior, and exit-code behavior.

Script-friendly validation command:

```powershell
godot-save-guard validate <fixtures> --schema <schema.json> --format json --output save-report.json --fail-on none
```

Generate a deterministic baseline fixture when a schema change needs a new
sample before hand-authored fixtures exist:

```powershell
godot-save-guard generate-fixture --schema <schema.json> --fixture-output <fixtures/generated-save.json> --set 'player.id="pilot-1"' --format json --output fixture-generation.json
```

The `migrate` and `migrate-chain` commands execute user-supplied command
templates. Use validation mode unless you intentionally want to run migrations.
When running a migration chain for real, pass `--schema` to validate each final
migrated fixture in the same report:

```powershell
godot-save-guard migrate-chain <fixtures> --chain migrations.toml --output-dir migrated --schema <schema.json> --compare-original --format json --output migration-chain.json
```

Use `--compare-original` when automation should surface how the final migrated
save differs from the original fixture without attaching large save files to a
report.

Before sharing fixtures outside your project, create reviewed sanitized copies:

```powershell
godot-save-guard redact <fixtures> --path player.name --path players.*.email --output-dir sanitized-fixtures --dry-run --format markdown
godot-save-guard redact <fixtures> --path player.name --path players.*.email --output-dir sanitized-fixtures --format json --output redaction-report.json
```

Reports can include save fixture paths and schema fields. Avoid publishing real
player saves or private fixtures. Redaction only changes the paths you list, so
review sanitized output before sharing it.
