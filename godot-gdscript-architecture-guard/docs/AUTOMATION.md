# Automation

Run the architecture guard in CI:

```powershell
godot-architecture-guard . --config architecture-guard.toml --format json --output reports\architecture.json
```

Generate SARIF when you want file-level annotations:

```powershell
godot-architecture-guard . --config architecture-guard.toml --format sarif --output reports\architecture.sarif
```

Use `--fail-on warning` only after the policy is stable. For first adoption,
`--fail-on error` is usually easier.

JSON output includes report metadata, rule explanations, and per-finding
suggestions. SARIF output uses the same rule descriptions for code-scanning
annotations.

For refactor review, JSON and Markdown output also include:

- `hotspots`: scripts with higher fan-in, fan-out, or autoload references.
- `possible_unused_scripts`: scripts with no visible `res://` reference or `class_name`
  declaration. Treat these as review candidates, not automatic deletion lists.
