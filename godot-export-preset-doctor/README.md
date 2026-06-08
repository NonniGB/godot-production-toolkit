# Godot Export Preset Doctor

Release-readiness checks for Godot `export_presets.cfg`, focused on Android, CI export hygiene, debug flags, signing safety, package identity, ABIs, icons, and missing export paths.

The tool is a companion to export automation. It does not build the game; it catches risky preset drift before a release job runs `godot --headless --export-release`.

## Install

```powershell
python -m pip install -e .
```

When published:

```powershell
python -m pip install godot-export-preset-doctor
```

## Quick Start

```powershell
godot-export-doctor C:\Projects\MyGame
godot-export-doctor . --platform Android
godot-export-doctor . --format sarif --output export-doctor.sarif
```

Use `--fail-on none` while exploring a report:

```powershell
godot-export-doctor examples\bad-export-project --fail-on none
```

## What It Checks

- Missing `export_presets.cfg`.
- Missing preset name, platform, or export path.
- Android package id, version code/name, enabled ABI, and launcher icon readiness.
- Release-like presets with debug options enabled.
- Hard-coded password, token, secret, or keystore-like values.
- JSON and SARIF output for automation.

## Configuration

Create `.godot-export-doctor.toml`:

```toml
format = "text"
fail_on = "warning"
platform = "Android"
required_android_abis = ["arm64-v8a"]
```

CLI flags override config values.

## Output

Text:

```powershell
godot-export-doctor .
```

JSON:

```powershell
godot-export-doctor . --format json --output export-report.json
```

SARIF:

```powershell
godot-export-doctor . --format sarif --output export-doctor.sarif
```

## Documentation

- [Android release checklist](docs/ANDROID_RELEASE_CHECKLIST.md)
- [Rule reference](docs/RULE_REFERENCE.md)
- [Security guide](docs/SECURITY_GUIDE.md)
- [Configuration](docs/CONFIGURATION.md)
- [CI integration](docs/CI.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## Development

```powershell
python -m pip install -e .
python -m unittest discover -s tests -v
godot-export-doctor examples\bad-export-project --fail-on none
```

## Design Notes

The checker is intentionally static. It reads Godot config files and reports conservative findings that are useful in local development and CI. It does not need the Godot editor, Android SDK, or network access.

Examples and fixtures are generic by design. They should be safe to publish without exposing private project details.
