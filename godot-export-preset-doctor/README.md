# Godot Export Preset Doctor

Release-readiness checks for Godot `export_presets.cfg`, focused on Android, CI export hygiene, debug flags, signing safety, package identity, ABIs, icons, and missing export paths.

The tool is a companion to export workflows. It does not build the game; it catches risky preset drift before a release job runs `godot --headless --export-release`.

Use it when a release preset changes, when setting up a new export target, or before cutting a public build from CI.

## Install

```powershell
python -m pip install -e .
```

From PyPI:

```powershell
python -m pip install godot-export-preset-doctor
```

## Quick Start

```powershell
godot-export-doctor C:\Projects\MyGame
godot-export-doctor . --platform Android
godot-export-doctor . --platform Android --required-android-abi arm64-v8a
godot-export-doctor . --format sarif --output export-doctor.sarif
godot-export-doctor matrix . --expected-platform Android --expected-platform Web --format markdown
godot-export-doctor leaks . --format html --output reports\export-leaks.html
godot-export-doctor diff . --baseline reports\baseline-export-presets --format markdown
godot-export-doctor inspect-folder build\android --format markdown
```

Use `--fail-on none` while exploring a report:

```powershell
godot-export-doctor examples\bad-export-project --fail-on none
```

## Real Workflow: Gate Release Presets In CI

Run the checker before a Godot export step so preset drift fails early:

```powershell
godot-export-doctor . --platform Android --fail-on warning --format sarif --output reports\export-doctor.sarif
```

This is especially useful for:

- catching debug flags that were left enabled in release-like presets;
- checking Android package id, version, icon, and ABI readiness;
- spotting local keystore paths or literal credential values before reports are shared;
- confirming export paths exist and match the expected target.

For a first pass on an existing project, avoid failing the build while you review findings:

```powershell
godot-export-doctor . --platform Android --fail-on none --format json --output reports\export-doctor.json
```

Require a specific Android ABI without creating a config file:

```powershell
godot-export-doctor . --platform Android --required-android-abi arm64-v8a --fail-on warning
```

## What It Checks

- Missing `export_presets.cfg`.
- Missing preset name, platform, or export path.
- Android package id, version code/name, enabled ABI, and launcher icon readiness.
- Release-like presets with debug options enabled.
- Hard-coded password, token, secret, or keystore-like values.
- Missing or duplicated expected export platforms in a release matrix.
- Export preset changes compared with a baseline.
- Broad export filters that may include debug/test/source files.
- Exported folders that contain debug/test/source-art/log/backup files.
- Local-looking export, include, or exclude paths that should not be shared in CI artifacts.
- JSON and SARIF output for scripts and CI, with plain-language rule explanations.

## Commands

`check` is the default command and keeps the original release-readiness behavior:

```powershell
godot-export-doctor check . --platform Android --format sarif --output reports\export.sarif
```

For older scripts, this is equivalent to:

```powershell
godot-export-doctor . --platform Android --format sarif --output reports\export.sarif
```

`matrix` gives a compact table of export presets and warns when an expected
platform is missing or duplicated:

```powershell
godot-export-doctor matrix . --expected-platform Android --expected-platform Web --format markdown
```

`leaks` checks broad export filters against common development-file patterns and
flags local-looking paths in preset fields:

```powershell
godot-export-doctor leaks . --format html --output reports\export-leaks.html --fail-on none
```

`diff` compares the current `export_presets.cfg` with a baseline project or
baseline preset file:

```powershell
godot-export-doctor diff . --baseline reports\baseline-export-presets --format markdown
```

`inspect-folder` scans an already-exported folder for development-looking files:

```powershell
godot-export-doctor inspect-folder build\android --format json --output reports\exported-folder.json
```

## Configuration

Create `.godot-export-doctor.toml`:

```toml
format = "text"
fail_on = "warning"
platform = "Android"
required_android_abis = ["arm64-v8a"]
allowed_secret_patterns = ["<.+>"]
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

JSON reports include report metadata, a rule catalog, and findings with readable
titles and explanations. This makes CI artifacts easier to review without
looking up every rule id.

Markdown or HTML matrix report:

```powershell
godot-export-doctor matrix . --expected-platform Android --expected-platform Web --format html --output export-matrix.html
```

SARIF:

```powershell
godot-export-doctor . --format sarif --output export-doctor.sarif
```

## CI Example

```yaml
- run: python -m pip install godot-export-preset-doctor
- run: godot-export-doctor . --platform Android --fail-on warning --format sarif --output reports/export-doctor.sarif
- run: godot-export-doctor matrix . --expected-platform Android --expected-platform Web --format markdown --output reports/export-matrix.md --fail-on warning
- run: godot-export-doctor leaks . --format html --output reports/export-leaks.html --fail-on warning
- run: godot-export-doctor diff . --baseline reports/baseline-export-presets --format markdown --output reports/export-diff.md --fail-on none
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
