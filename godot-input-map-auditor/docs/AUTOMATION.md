# Script And CI Usage

Read `tool-manifest.json` first. It declares the CLI entry point, module entry point, output formats, write behavior, and exit-code behavior.

Script-friendly command:

```powershell
godot-input-audit <project> --require keyboard,touch --format json --output input-report.json --fail-on none
```

Generate docs and constants when requested:

```powershell
godot-input-audit <project> --write-docs docs/INPUT_REFERENCE.md --generate-gd scripts/generated/input_actions.gd
```

The tool reads `project.godot` only and does not execute project code.
