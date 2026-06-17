# Godot Save Schema Guard

Validate Godot save-game fixtures against explicit schemas and catch incompatible save format changes before release.

The first release focuses on JSON saves because they are deterministic to validate outside the engine. It is meant to be a release gate: do not break player saves.

## Install

```powershell
python -m pip install -e .
```

When published:

```powershell
python -m pip install godot-save-schema-guard
```

## Quick Start

```powershell
godot-save-guard generate-fixture --schema schemas\save.schema.json --fixture-output saves\fixtures\generated_v3.json --set 'player.id="pilot-1"' --format markdown
godot-save-guard validate saves\fixtures --schema schemas\save.schema.json
godot-save-guard validate examples\fixtures --schema examples\schema\save.schema.json --format markdown --output SAVE_COMPATIBILITY.md
godot-save-guard migrate saves\v1 --output-dir migrated\v2 --command "godot --headless --script tools/migrate_save.gd --input {input} --output {output}"
godot-save-guard migrate-chain saves\v1 --chain migrations.toml --output-dir migrated --schema schemas\save.schema.json --compare-original --format json --output reports\migration-chain.json
godot-save-guard migration-graph --chain migrations.toml --current 3 --supported 1 --supported 2 --format markdown
godot-save-guard redact saves\fixtures --path player.name --path players.*.email --output-dir sanitized\saves --dry-run
```

## What It Checks

- Invalid JSON fixtures.
- Missing top-level `version`.
- Missing required schema properties.
- Numeric type drift such as `"100"` where a number is expected.
- Type mismatches.
- Unexpected properties when `additionalProperties` is false.
- Generated fixture samples from required schema fields, defaults, enum values, and optional JSON overrides.
- Migration command failures.
- Ordered migration chains from older save versions to the current format.
- Final migrated fixture validation after a migration chain succeeds.
- Before-and-after summaries that compare original fixtures with final migrated outputs.
- Missing migration paths from supported save versions to the current format.
- Selected-field redaction for sanitized fixture copies.
- Report metadata and plain-language rule explanations for compatibility findings.

Redaction is path-based. It only changes paths you list with `--path`, so review
sanitized fixtures before attaching them to issues, documentation, or reports.

## Documentation

- [Schema guide](docs/SCHEMA_GUIDE.md)
- [Migration workflow](docs/MIGRATIONS.md)
- [Godot JSON caveats](docs/GODOT_JSON_CAVEATS.md)
- [Rule reference](docs/RULE_REFERENCE.md)
- [CI usage](docs/CI.md)

## Development

```powershell
python -m pip install -e .
python -m unittest discover -s tests -v
godot-save-guard validate examples\fixtures --schema examples\schema\save.schema.json --fail-on none
```

Fixtures are generic and intentionally small so the repository is safe to publish.
