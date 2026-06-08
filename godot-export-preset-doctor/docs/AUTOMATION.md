# Automation Usage

Read `tool-manifest.json` first. It declares the CLI entry point, module entry point, output formats, write behavior, and exit-code behavior.

Automation-friendly command:

```powershell
godot-export-doctor <project> --platform Android --format json --output export-report.json --fail-on none
```

Use SARIF when integrating with code scanning:

```powershell
godot-export-doctor <project> --format sarif --output export-doctor.sarif --fail-on error
```

Credential-like values are redacted in findings. Review reports before sharing because preset names and local paths may still be private.
