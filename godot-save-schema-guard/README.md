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
godot-save-guard validate saves\fixtures --schema schemas\save.schema.json
godot-save-guard validate examples\fixtures --schema examples\schema\save.schema.json --format markdown --output SAVE_COMPATIBILITY.md
godot-save-guard migrate saves\v1 --output-dir migrated\v2 --command "godot --headless --script tools/migrate_save.gd --input {input} --output {output}"
```

## What It Checks

- Invalid JSON fixtures.
- Missing top-level `version`.
- Missing required schema properties.
- Numeric type drift such as `"100"` where a number is expected.
- Type mismatches.
- Unexpected properties when `additionalProperties` is false.
- Migration command failures.

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
