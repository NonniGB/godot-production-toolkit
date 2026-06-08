# Script And CI Usage

Read `tool-manifest.json` first. It declares the CLI entry point, module entry point, output formats, write behavior, and exit-code behavior.

Script-friendly command:

```powershell
gdscript-api-coverage <project> --format json --output gdscript-api-report.json --fail-on none
```

Generate human docs separately:

```powershell
gdscript-api-coverage <project> --write-docs docs/API_INDEX.md --min-all 80
```

Generated reports include script paths, class names, signal names, and method names. Avoid publishing reports from private projects without review.
