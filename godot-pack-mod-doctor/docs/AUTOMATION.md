# Automation

Generate a manifest from a pack folder:

```powershell
godot-pack-mod-doctor manifest from-folder addons\demo_pack --id demo_pack --version 1.0.0 --output pack-manifest.json
```

Check a pack manifest during CI:

```powershell
godot-pack-mod-doctor check pack-manifest.json --format json --output reports\pack.json
```

Check references against a base content manifest:

```powershell
godot-pack-mod-doctor check pack-manifest.json --base base-content.json --format markdown --output reports\pack.md
```

Treat advisory file-policy warnings as CI failures:

```powershell
godot-pack-mod-doctor check pack-manifest.json --format json --fail-on warning
```

Exit codes:

- `0`: no findings at the selected fail threshold.
- `1`: findings met the selected fail threshold.
- `2`: command-line usage error.
