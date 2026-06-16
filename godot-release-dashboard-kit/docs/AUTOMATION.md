# Automation

Build an HTML dashboard artifact from existing reports:

```powershell
godot-release-dashboard build reports\godot-project-doctor --output reports\dashboard.html
```

Build a JSON summary for downstream scripts:

```powershell
godot-release-dashboard build reports\godot-project-doctor --format json --output reports\dashboard.json
```

Exit codes:

- `0`: dashboard written.
- `2`: command-line usage error.
