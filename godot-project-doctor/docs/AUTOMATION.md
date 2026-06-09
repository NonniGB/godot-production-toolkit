# Script And CI Usage

Use `plan` or `run --dry-run` before executing checks. These commands are noninteractive and do not create report directories.

```powershell
godot-project-doctor plan godot-project-doctor.toml --format json
godot-project-doctor run --project . --checks assets,export --reports-dir reports --dry-run --format json
```

Run checks only after reviewing the planned commands:

```powershell
godot-project-doctor run godot-project-doctor.toml --format markdown --output reports\summary.md
```

Use JSON for planning and HTML or Markdown when someone needs to read the report.

Compare report folders when a job keeps a previous run as an artifact:

```powershell
godot-project-doctor compare reports\baseline reports\current --format markdown --fail-on warning
```

Use `--fail-on error` when only new errors should fail the job.
