# CI Usage

```yaml
- name: Install pixel space assets
  run: python -m pip install pixel-space-asset-toolkit

- name: Regenerate deterministic preview
  run: |
    pixel-space-assets asteroid-hex --material ferric --count 16 --size 64 --seed 7 --output generated/ferric
    pixel-space-assets preview generated/ferric --output generated/ferric_preview.png

- name: Compare generated sprite preview
  run: pixel-space-assets compare baseline/ferric_preview.png generated/ferric_preview.png --diff-output reports/ferric_diff.png --fail-on-diff --format json

- name: Compare generated sprite set
  run: pixel-space-assets compare-dir baseline/ferric generated/ferric --diff-output-dir reports/ferric_diffs --fail-on-diff --format json

- name: Compare generated sprite manifests
  run: pixel-space-assets compare-manifest baseline/ferric/manifest.json generated/ferric/manifest.json --diff-output-dir reports/ferric_manifest_diffs --fail-on-diff --format json
```

Commit generated outputs only when they are intentional assets or documentation fixtures.
