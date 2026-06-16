# Godot Save Migration Testing

Use this when changing save-game fields, save versions, inventory data, quest
state, player settings, or any migration script that rewrites old saves. The
goal is to prove that old fixtures still validate and that migration commands
produce files matching the current schema.

Related docs: [Tool Index](../TOOL_INDEX.md) and [Use Cases](../USE_CASES.md).

## Packages

- `godot-save-schema-guard` for schema validation and migration-chain checks.

## Copy-paste commands

```powershell
python -m pip install godot-save-schema-guard
godot-save-guard validate saves\fixtures --schema schemas\save.schema.json --format markdown --output reports\save-validation.md
godot-save-guard migration-graph --chain migrations.toml --current 3 --supported 1 --supported 2 --format markdown --output reports\save-migration-graph.md
godot-save-guard redact saves\fixtures --path player.name --path players.*.email --output-dir reports\sanitized-saves --dry-run --format markdown --output reports\save-redaction-plan.md
godot-save-guard migrate-chain saves\v1 --chain migrations.toml --output-dir reports\migrated-saves --dry-run --format markdown --output reports\save-migration-plan.md
```

Run the migration chain for real after reviewing the dry run:

```powershell
godot-save-guard migrate-chain saves\v1 --chain migrations.toml --output-dir reports\migrated-saves --format json --output reports\save-migration.json
godot-save-guard validate reports\migrated-saves --schema schemas\save.schema.json --format json --output reports\migrated-save-validation.json
```

## Expected inputs

- Save fixtures from one or more older versions.
- A JSON schema for the current save format.
- Optional `migrations.toml` describing migration steps.
- Optional project migration commands referenced by the migration chain.

## Expected outputs

- Validation reports for existing and migrated saves.
- A dry-run migration plan before files are written.
- A redaction plan and optional sanitized fixture copies when fixtures need to be
  shared outside the project.
- Migrated save files in the selected output directory when the real migration runs.
