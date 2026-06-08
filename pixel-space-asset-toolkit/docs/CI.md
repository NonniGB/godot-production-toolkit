# CI Usage

```yaml
- name: Install pixel space assets
  run: python -m pip install pixel-space-asset-toolkit

- name: Regenerate deterministic preview
  run: |
    pixel-space-assets asteroid-hex --material ferric --count 16 --size 64 --seed 7 --output generated/ferric
    pixel-space-assets preview generated/ferric --output generated/ferric_preview.png
```

Commit generated outputs only when they are intentional assets or documentation fixtures.
