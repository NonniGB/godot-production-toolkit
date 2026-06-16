# Godot Mod DLC Pack Validation

Use this before shipping a Godot patch, DLC pack, mod package, or optional
content bundle. It checks the pack manifest for identity fields, duplicate
paths, unexpected overrides, and references that do not exist in the base
manifest.

Related docs: [Tool Index](../TOOL_INDEX.md) and [Use Cases](../USE_CASES.md).

## Packages

- `godot-pack-mod-doctor` for pack, patch, DLC, and mod manifest checks.
- `godot-content-graph-doctor` when pack content also needs reference graph checks.

## Copy-paste commands

```powershell
python -m pip install godot-pack-mod-doctor
godot-pack-mod-doctor check pack-manifest.json --format markdown --output reports\pack.md
godot-pack-mod-doctor check pack-manifest.json --base base-content.json --format json --output reports\pack.json
godot-pack-mod-doctor diff baseline-pack.json current-pack.json --format markdown --output reports\pack-diff.md
godot-pack-mod-doctor load-order base-pack.json current-pack.json --format markdown --output reports\pack-load-order.md
```

Add content graph checks when the pack includes data files with ids and references:

```powershell
godot-content-graph . --preset packs --format markdown --output reports\pack-content.md --fail-on none
```

## Expected inputs

- A pack manifest JSON file.
- Optional base manifest JSON for override and reference checks.
- Optional content folders when running a separate content graph pass.

## Expected outputs

- Markdown or JSON pack validation reports.
- Findings for duplicate paths, missing identity fields, unexpected overrides, missing references, pack diffs, and load-order conflicts.
- A CI-friendly exit code based on the selected failure threshold.
