# CI Usage

```yaml
- name: Install localization guard
  run: python -m pip install godot-localization-qa-guard

- name: Check localization
  run: godot-l10n-guard . --translations translations --require fr,es,de --scan-scripts --scan-scenes --format markdown --output docs/LOCALIZATION_QA.md
```

Use `--fail-on error` during early adoption if unchanged-string and unused-key warnings are too noisy.

Add layout-oriented checks when translations are close to release:

```yaml
- name: Check localization layout risk
  run: godot-l10n-guard . --translations translations --max-expansion 1.35 --allowed-glyphs-file fonts/ui-glyphs.txt --format json --output reports/localization-layout.json --fail-on warning
```
