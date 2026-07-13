# CI Usage

```yaml
- name: Install visual smoke kit
  run: python -m pip install godot-visual-smoke-test-kit

- name: Compare screenshots
  run: godot-visual-smoke compare baselines/menu.png current/menu.png --diff diffs/menu.png --format json --output visual-report.json
```

Upload `current`, `diffs`, and `visual-report.json` as CI artifacts.
When a baseline or current screenshot is missing, the JSON report still uses the
normal findings shape so the job log can point to the missing file instead of a
traceback.

JSON output keeps the basic diff fields at the top level and also includes
metadata, a rule catalog, and readable failure explanations. That makes the same
report useful in scripts and in artifact review.
