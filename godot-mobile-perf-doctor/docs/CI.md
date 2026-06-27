# CI Usage

```yaml
- name: Install mobile perf doctor
  run: python -m pip install godot-mobile-perf-doctor

- name: Static mobile diagnostics
  run: godot-mobile-perf-doctor . --static --mobile-ui-metadata reports/mobile-ui.json --format markdown --output mobile-perf-report.md
```

Use `--fail-on error` if warnings are too noisy during initial adoption.
