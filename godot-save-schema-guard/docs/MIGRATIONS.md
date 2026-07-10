# Migration Workflow

Create a small baseline fixture when the schema changed but fixture coverage has
not caught up yet:

```powershell
godot-save-guard generate-fixture --schema schemas\save.schema.json --fixture-output saves\fixtures\generated_v3.json --set 'player.id="pilot-1"' --format markdown
```

By default, generated fixtures include required properties. Add
`--include-optional` when you want a fuller sample that also covers optional
schema properties. Use repeated `--set dotted.path=json_value` flags for stable
IDs or values that make the fixture easier to recognize in reports.

Build command templates with `{input}` and `{output}`:

```powershell
godot-save-guard migrate saves\v1 --output-dir migrated\v2 --timeout 120 --command "godot --headless --script tools/migrate_save.gd --input {input} --output {output}"
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
godot-save-guard migrate-chain saves\v1 --chain migrations.toml --output-dir migrated --schema schemas\save.schema.json --compare-original --format json --output reports\migration-chain.json
```

Each step writes an intermediate output named after the original fixture and
target version, such as `save.v2.json` and `save.v3.json`.

Commands run directly, without a system shell. Use a program and arguments in
the template; shell operators such as pipes, redirects, and `&&` are not
supported. `{input}` and `{output}` are kept as single arguments even when paths
contain spaces. Nested fixture folders are preserved below the output folder,
so two fixtures with the same filename cannot overwrite each other. Use
`--timeout` to change the 120-second limit for each command or chain step.

When `--schema` is provided, the command validates the final migrated output
with the same save-compatibility rules used by `validate`. That catches cases
where a migration script exits cleanly but writes a save shape the current game
cannot load.

Add `--compare-original` when reviewers also need a compact before-and-after
summary of added, removed, and changed JSON paths.

If a chain step fails, the report names the step, original fixture, expected
output path, and captured stdout/stderr snippets from the project migration
command when they are available. That gives CI logs enough context to identify
which migration script needs review without attaching full save files.
