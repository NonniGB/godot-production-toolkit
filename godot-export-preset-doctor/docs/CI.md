# CI Integration

Install the package and run it before the export step:

```yaml
- name: Install export doctor
  run: python -m pip install godot-export-preset-doctor

- name: Check export presets
  run: godot-export-doctor . --platform Android --required-android-abi arm64-v8a --format sarif --output export-doctor.sarif
```

Use `--fail-on error` if warnings are too noisy during initial adoption. For release branches, `--fail-on warning` is recommended.

If your project keeps harmless placeholders in `export_presets.cfg` and injects real secrets in CI, allow only the placeholder shape:

```yaml
- run: godot-export-doctor . --platform Android --allow-secret-pattern "<.+>" --fail-on warning
```

The tool is a companion to Godot export actions. It does not build the game; it checks that the export preset is ready before another step invokes `godot --headless --export-release`.

JSON and SARIF reports include readable rule names and explanations. Keep the
report as a CI artifact when a failed export check needs review outside the job
log.
