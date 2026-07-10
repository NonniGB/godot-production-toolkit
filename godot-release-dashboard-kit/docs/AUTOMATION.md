# Automation

Malformed reports, invalid summary counts, and unreadable image artifacts are
represented as blocked dashboard inputs instead of being skipped or treated as
ready.

Build an HTML dashboard artifact from existing reports:

```powershell
godot-release-dashboard build reports\godot-project-doctor --output reports\dashboard.html
```

Compare a current reports folder with the previous run or previous release:

```powershell
godot-release-dashboard build reports\current --previous-reports-dir reports\previous --output reports\dashboard.html
```

Add scenario evidence that has already been produced by a runner:

```powershell
godot-scenario-report bundle reports\scenarios --manifest scenario-manifest.json --telemetry reports\runtime-timeline.json --evidence log=reports\run.log --evidence junit=reports\junit.xml --format json --output reports\release-evidence\scenario-bundle.json
godot-release-dashboard build reports\release-evidence --output reports\dashboard.html
```

The dashboard collects source report links and bundle metadata for review. It
does not start Godot, run scenarios, copy logs, or rewrite evidence files.
Scenario bundle telemetry summaries are shown as compact frame, sample, and
spike metrics. If a JSON report records a reproduction command, the dashboard
shows that command as supplied by the report; it does not execute it.
Workflow and category labels are read from report metadata and used only to
organize the dashboard. Review generated dashboards before sharing them because
source reports may contain local paths, branch names, machine names, or command
arguments.
Previous-report comparisons only read the previous folder. They are intended for
small release-history summaries, not for storing private logs in the dashboard
repository.

Build a JSON summary for downstream scripts:

```powershell
godot-release-dashboard build reports\godot-project-doctor --format json --output reports\dashboard.json
```

Exit codes:

- `0`: dashboard written.
- `2`: command-line usage error.
