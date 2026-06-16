# Godot Pack Mod Doctor

`godot-pack-mod-doctor` validates small Godot pack, patch, DLC, and mod
manifests before release. It is intentionally format-light: projects keep their
own build system, while the tool checks the manifest evidence that build system
emits.

## Install

```powershell
python -m pip install godot-pack-mod-doctor
```

From a source checkout:

```powershell
python -m pip install -e .\godot-pack-mod-doctor
```

## Quick Start

```powershell
godot-pack-mod-doctor check pack-manifest.json --format markdown
godot-pack-mod-doctor check pack-manifest.json --base base-content.json --format json --output reports\pack.json
```

## Manifest Shape

```json
{
  "id": "demo_patch",
  "version": "1.0.0",
  "dependencies": [{"id": "base_game", "version": ">=1.0.0"}],
  "files": [
    {
      "path": "res://content/items/sword.tres",
      "references": ["iron_ingot"],
      "overrides": false
    }
  ]
}
```

The optional base manifest can contain `content` entries with `id` fields.

## Checks

- missing pack id or version;
- file entries without paths;
- duplicate shipped paths;
- unexpected overrides;
- references that are not present in a supplied base content manifest.

## Outputs

- `text`: local terminal report.
- `json`: CI and scripts.
- `markdown`: PR comments and release notes.
