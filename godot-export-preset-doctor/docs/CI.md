# CI Integration

Install the package and run it before the export step:

```yaml
- name: Install export doctor
  run: python -m pip install godot-export-preset-doctor

- name: Check export presets
  run: godot-export-doctor . --platform Android --required-android-abi arm64-v8a --format sarif --output export-doctor.sarif

- name: Check release target matrix
  run: godot-export-doctor matrix . --expected-platform Android --expected-platform Web --format markdown --output export-matrix.md --fail-on warning

- name: Check export preset leak risks
  run: godot-export-doctor leaks . --format html --output export-leaks.html --fail-on warning

- name: Inspect exported folder
  run: godot-export-doctor inspect-folder build/android --hash-files --format json --output exported-folder.json --fail-on none
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

Matrix and leak reports are useful as normal workflow artifacts. The matrix
shows which presets exist for the expected release targets, while the leak
report highlights broad filters and local-looking paths before those details
end up in shared build logs.

For projects that can emit an exported file list, `inspect-files` is a lighter
alternative to scanning the built folder:

```yaml
- run: godot-export-doctor inspect-files reports/export-file-list.json --format markdown --output exported-files.md --fail-on none
```

Direct binary `.pck` parsing is intentionally not supported. Generate a file
list during your export pipeline and inspect that reviewable text or JSON
artifact instead.
