# Godot Mod DLC Pack Validation

Use this before shipping a Godot patch, DLC pack, mod package, or optional
content bundle. It checks the pack manifest for identity fields, dependency
entries, duplicate paths, unexpected overrides, and references that do not
exist in the base manifest. It can also generate a reviewable manifest from a
folder before the check step runs.

Related docs: [Tool Index](../TOOL_INDEX.md) and [Use Cases](../USE_CASES.md).

## Packages

- `godot-pack-mod-doctor` for pack, patch, DLC, and mod manifest checks.
- `godot-content-graph-doctor` when pack content also needs reference graph checks.

## Copy-paste commands

```powershell
python -m pip install godot-pack-mod-doctor
godot-pack-mod-doctor manifest from-folder addons\demo_pack --id demo_pack --version 1.0.0 --output pack-manifest.json
godot-pack-mod-doctor check pack-manifest.json --format markdown --output reports\pack.md
godot-pack-mod-doctor check pack-manifest.json --base base-content.json --format json --output reports\pack.json
godot-pack-mod-doctor diff baseline-pack.json current-pack.json --format markdown --output reports\pack-diff.md
godot-pack-mod-doctor load-order base-pack.json current-pack.json optional-mod.json --format markdown --output reports\pack-load-order.md
```

Add content graph checks when the pack includes data files with ids and references:

```powershell
godot-content-graph . --preset packs --format markdown --output reports\pack-content.md --fail-on none
```

## Expected inputs

- A pack manifest JSON file.
- Optional pack folder when generating a manifest from shipped resources.
- Optional base manifest JSON for override and reference checks.
- Optional content folders when running a separate content graph pass.

## Expected outputs

- Markdown or JSON pack validation reports.
- Generated manifests with `res://` paths, file sizes, and SHA-256 hashes.
- Findings for duplicate paths, missing identity fields, non-portable paths,
  case-only collisions, files that need manual review, unexpected overrides,
  missing references, pack diffs, missing dependencies, dependency order
  problems, duplicate pack ids, and load-order conflicts.
- A CI-friendly exit code based on the selected failure threshold.
