# Godot Android Export CI

Use this when Android export settings need to be checked in CI before an APK or
AAB build. It catches common Godot Android release problems such as missing
package identifiers, debug flags, version fields, ABI expectations, and mobile
project settings that are easy to miss in the editor.

Related docs: [Tool Index](../TOOL_INDEX.md) and [Use Cases](../USE_CASES.md).

## Packages

- `godot-export-preset-doctor` for `export_presets.cfg`.
- `godot-mobile-perf-doctor` for Android-friendly project settings.
- `godot-project-doctor` when the Android checks should be part of a larger CI report.

## Copy-paste commands

```powershell
python -m pip install godot-export-preset-doctor godot-mobile-perf-doctor
godot-export-doctor . --platform Android --required-android-abi arm64-v8a --format sarif --output reports\android-export.sarif
godot-export-doctor diff . --baseline reports\baseline-export-presets --format markdown --output reports\android-export-diff.md --fail-on none
godot-mobile-perf-doctor . --static --format markdown --output reports\android-mobile-settings.md
```

For a softer first run that reports findings without failing CI:

```powershell
godot-export-doctor . --platform Android --required-android-abi arm64-v8a --fail-on none --format json --output reports\android-export.json
```

## Expected inputs

- A Godot project root containing `project.godot`.
- `export_presets.cfg` with an Android preset.
- Optional `.godot-export-doctor.toml` for allowed patterns and project rules.

## Expected outputs

- SARIF, JSON, or Markdown reports under `reports`.
- Findings for missing or risky Android export fields.
- A non-zero exit code when the configured severity threshold is reached.
