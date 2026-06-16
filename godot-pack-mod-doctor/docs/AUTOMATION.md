# Automation

Check a pack manifest during CI:

```powershell
godot-pack-mod-doctor check pack-manifest.json --format json --output reports\pack.json
```

Check references against a base content manifest:

```powershell
godot-pack-mod-doctor check pack-manifest.json --base base-content.json --format markdown --output reports\pack.md
```

Exit codes:

- `0`: no findings at the selected fail threshold.
- `1`: findings met the selected fail threshold.
- `2`: command-line usage error.
