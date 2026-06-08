# Migration Workflow

Build command templates with `{input}` and `{output}`:

```powershell
godot-save-guard migrate saves\v1 --output-dir migrated\v2 --command "godot --headless --script tools/migrate_save.gd --input {input} --output {output}"
```

The first release records command failures. A later release can validate migrated output against a target schema in the same command.
