# Automation

Build an HTML dashboard artifact from existing reports:

```powershell
godot-release-dashboard build reports\godot-project-doctor --output reports\dashboard.html
```

Add scenario evidence that has already been produced by a runner:

```powershell
godot-scenario-report bundle reports\scenarios --manifest scenario-manifest.json --evidence log=reports\run.log --evidence junit=reports\junit.xml --format json --output reports\release-evidence\scenario-bundle.json
godot-release-dashboard build reports\release-evidence --output reports\dashboard.html
```

The dashboard collects source report links and bundle metadata for review. It
does not start Godot, run scenarios, copy logs, or rewrite evidence files.

Build a JSON summary for downstream scripts:

```powershell
godot-release-dashboard build reports\godot-project-doctor --format json --output reports\dashboard.json
```

Exit codes:

- `0`: dashboard written.
- `2`: command-line usage error.
