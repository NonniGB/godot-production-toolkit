# CI Integration

Install the package and run it before export automation:

```yaml
- name: Install export doctor
  run: python -m pip install godot-export-preset-doctor

- name: Check export presets
  run: godot-export-doctor . --platform Android --format sarif --output export-doctor.sarif
```

Use `--fail-on error` if warnings are too noisy during initial adoption. For release branches, `--fail-on warning` is recommended.

The tool is a companion to Godot export actions. It does not build the game; it checks that the export preset is ready before another step invokes `godot --headless --export-release`.
