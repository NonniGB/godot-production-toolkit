# Migration Workflow

Build command templates with `{input}` and `{output}`:

```powershell
godot-save-guard migrate saves\v1 --output-dir migrated\v2 --command "godot --headless --script tools/migrate_save.gd --input {input} --output {output}"
```

For projects with several released save versions, define an ordered migration
chain:

```toml
[[steps]]
from = "1"
to = "2"
command = "godot --headless --script tools/migrate_v1_v2.gd --input {input} --output {output}"

[[steps]]
from = "2"
to = "3"
command = "godot --headless --script tools/migrate_v2_v3.gd --input {input} --output {output}"
```

Check the chain without running commands:

```powershell
godot-save-guard migrate-chain saves\v1 --chain migrations.toml --output-dir migrated --dry-run --format markdown
```

Check that every supported save version can reach the current format:

```powershell
godot-save-guard migration-graph --chain migrations.toml --current 3 --supported 1 --supported 2 --format markdown --output reports\migration-graph.md
```

Run the chain:

```powershell
godot-save-guard migrate-chain saves\v1 --chain migrations.toml --output-dir migrated --format json --output reports\migration-chain.json
```

Each step writes an intermediate output named after the original fixture and
target version, such as `save.v2.json` and `save.v3.json`.

After running the chain, validate the migrated output with the normal
`validate` command and the target schema.
