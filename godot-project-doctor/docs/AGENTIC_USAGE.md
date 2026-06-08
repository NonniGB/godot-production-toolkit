# Agentic Usage

Use `plan` or `run --dry-run` before executing checks. These commands are noninteractive and do not create report directories.

```powershell
godot-project-doctor plan godot-project-doctor.toml --format json
godot-project-doctor run --project . --checks assets,export --reports-dir reports --dry-run --format json
```

Run checks only after reviewing the planned commands:

```powershell
godot-project-doctor run godot-project-doctor.toml --format markdown --output reports\summary.md
```

Agents should prefer JSON for planning and HTML or Markdown for handoff reports.
