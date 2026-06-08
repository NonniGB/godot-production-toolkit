# CI Usage

```yaml
- name: Install localization guard
  run: python -m pip install godot-localization-qa-guard

- name: Check localization
  run: godot-l10n-guard . --translations translations --require fr,es,de --scan-scripts --scan-scenes --format markdown --output docs/LOCALIZATION_QA.md
```

Use `--fail-on error` during early adoption if unchanged-string and unused-key warnings are too noisy.
