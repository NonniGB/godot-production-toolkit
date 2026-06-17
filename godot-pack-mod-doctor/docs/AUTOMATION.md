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

Review content-pack load order before publishing a mod set:

```powershell
godot-pack-mod-doctor load-order base-pack.json patch-pack.json optional-mod.json --format markdown --output reports\pack-load-order.md
```

Review what changed between two pack releases:

```powershell
godot-pack-mod-doctor diff baseline-pack.json current-pack.json --format markdown --output reports\pack-diff.md
```

The JSON reports include `summary.risk_level`, `summary.risk_score`, and a
`risk` object so dashboards can highlight blocked or attention-needed pack
reports without custom parsing.

Exit codes:

- `0`: no findings at the selected fail threshold.
- `1`: findings met the selected fail threshold.
- `2`: command-line usage error.
