# CI Usage

```yaml
- name: Install save guard
  run: python -m pip install godot-save-schema-guard

- name: Validate save fixtures
  run: godot-save-guard validate saves/fixtures --schema schemas/save.schema.json --format markdown --output docs/SAVE_COMPATIBILITY.md
```

When a schema changed and you need a quick fixture to review or extend:

```yaml
- name: Generate baseline save fixture
  run: godot-save-guard generate-fixture --schema schemas/save.schema.json --fixture-output saves/fixtures/generated-current.json --format markdown --output reports/save-fixture-generation.md
```

When migration commands are part of the release, validate the final migrated
save shape in the same job:

```yaml
- name: Run save migrations and validate output
  run: godot-save-guard migrate-chain saves/v1 --chain migrations.toml --output-dir reports/migrated-saves --schema schemas/save.schema.json --compare-original --format json --output reports/save-migration.json
```

`--compare-original` adds a compact before-and-after summary that is useful in
dashboards and pull request notes.

When CI uploads sample fixtures as artifacts, write sanitized copies first:

```yaml
- name: Redact shared save fixtures
  run: godot-save-guard redact saves/fixtures --path player.name --path players.*.email --output-dir reports/sanitized-saves --format json --output reports/save-redaction.json
```

Keep at least one fixture per released save version.

JSON and Markdown reports include readable rule explanations. Keep the report as
a CI artifact when save compatibility failures need review outside the job log.
