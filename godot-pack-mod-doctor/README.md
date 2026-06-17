# Godot Pack Mod Doctor

`godot-pack-mod-doctor` generates and validates small Godot pack, patch, DLC,
and mod manifests before release. It is intentionally format-light: projects
keep their own build system, while the tool checks the manifest evidence that
build system emits.

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
godot-pack-mod-doctor manifest from-folder addons\demo_pack --id demo_pack --version 1.0.0 --output pack-manifest.json
godot-pack-mod-doctor check pack-manifest.json --format markdown
godot-pack-mod-doctor check pack-manifest.json --base base-content.json --format json --output reports\pack.json
godot-pack-mod-doctor diff baseline-pack.json current-pack.json --format markdown
godot-pack-mod-doctor load-order base-pack.json patch-pack.json optional-mod.json --format markdown
```

`manifest from-folder` writes a reviewable JSON manifest from a folder of pack
files. It records deterministic `res://` paths, byte sizes, and SHA-256 hashes
so later `diff` reports can show exactly which shipped resources changed.

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
      "overrides": false,
      "size": 128,
      "sha256": "..."
    }
  ]
}
```

The optional base manifest can contain `content` entries with `id` fields.
Dependencies can be written as objects with an `id` field, or as simple id
strings when version constraints are tracked elsewhere.

## Checks

- missing pack id or version;
- malformed or duplicated dependency entries;
- file entries without paths;
- duplicate shipped paths;
- unexpected overrides;
- references that are not present in a supplied base content manifest;
- local, parent-directory, or non-`res://` paths;
- case-only path collisions that can break on Windows or macOS;
- script, native binary, archive, packed-project, debug, backup, cache, or key
  files that commonly need manual review before public distribution;
- added, removed, and changed files between two pack manifests;
- duplicate pack ids, missing dependencies, dependency order problems, and
  undeclared override conflicts across ordered packs.

Scripted mods and native extensions can be legitimate. These file policy checks
are warnings by default; use `--fail-on warning` in CI if your project wants a
stricter content-pack gate.

## Outputs

- `text`: local terminal report.
- `json`: CI and scripts.
- `markdown`: PR comments and release notes.

`diff` is useful before publishing a patch or DLC update. It compares shipped
paths and stable file metadata so changed resources are visible in review.

`load-order` reads packs in the order supplied on the command line. If a later
pack ships the same resource path without setting `overrides: true`, the report
flags the conflict so the intended ownership is explicit. It also checks that
dependencies listed by each pack are present earlier in the supplied load order.
