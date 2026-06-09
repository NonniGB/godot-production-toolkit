# CI Usage

```yaml
- name: Install save guard
  run: python -m pip install godot-save-schema-guard

- name: Validate save fixtures
  run: godot-save-guard validate saves/fixtures --schema schemas/save.schema.json --format markdown --output docs/SAVE_COMPATIBILITY.md
```

Keep at least one fixture per released save version.

JSON and Markdown reports include readable rule explanations. Keep the report as
a CI artifact when save compatibility failures need review outside the job log.
