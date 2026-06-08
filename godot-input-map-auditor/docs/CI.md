# CI Usage

```yaml
- name: Install input auditor
  run: python -m pip install godot-input-map-auditor

- name: Audit input map
  run: godot-input-audit . --require keyboard,touch --write-docs docs/INPUT_REFERENCE.md
```

For desktop-only projects, use:

```powershell
godot-input-audit . --require keyboard,mouse
```

For mobile-first projects, `touch` should usually be required for player-facing actions.
