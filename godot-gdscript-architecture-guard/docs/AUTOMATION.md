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

