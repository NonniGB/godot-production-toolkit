# Automation Usage

Read `tool-manifest.json` first. It declares the CLI entry point, module entry point, output formats, write behavior, and exit-code behavior.

Automation-friendly capture planning:

```powershell
godot-visual-smoke plan visual-smoke.toml --project <project> --format json
```

Automation-friendly screenshot comparison:

```powershell
godot-visual-smoke compare <baseline.png> <current.png> --diff <diff.png> --format json --output visual-report.json --fail-on none
```

Screenshots and diff images can reveal private UI or unreleased art. Review images before publishing.
