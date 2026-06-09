# Godot Content Graph Doctor

`godot-content-graph-doctor` validates data-driven content used by Godot
projects. It is useful when items, recipes, quests, dialogue, enemies, levels,
or content packs live in JSON, CSV, or TOML files.

It does not need the Godot editor. It reads content files, checks ids and
references, and produces reports that work locally or in CI.

## Install

```powershell
python -m pip install godot-content-graph-doctor
```

From a source checkout:

```powershell
python -m pip install -e .\godot-content-graph-doctor
```

## Quick Start

```powershell
godot-content-graph examples\tiny-content-project --config content-graph.toml
```

Write machine-readable output:

```powershell
godot-content-graph examples\tiny-content-project --config content-graph.toml --format json --output reports\content-graph.json
```

Create a Mermaid graph:

```powershell
godot-content-graph examples\tiny-content-project --config content-graph.toml --format mermaid --fail-on none
```

## Config Example

```toml
[collections.items]
path = "data/items.json"
id = "id"
roots = ["copper_ore"]
warn_unused = true
numeric_fields = ["value"]

[collections.recipes]
path = "data/recipes.json"
id = "id"
numeric_fields = ["craft_time"]

[[collections.recipes.references]]
field = "inputs[].item"
collection = "items"

[[collections.recipes.references]]
field = "outputs[].item"
collection = "items"
```

Each collection points to one file. JSON may be a list of objects or an object
containing `items`, `data`, `rows`, or a key matching the collection name. CSV
uses the header row. TOML uses `items`, `data`, `rows`, or the collection name.

Reference fields support simple dotted paths and list traversal with `[]`, such
as `inputs[].item`.

## Checks

- missing or duplicate ids;
- references to ids that do not exist in the target collection;
- unused ids when `warn_unused = true`;
- numeric field summaries and transparent outlier warnings.

## Outputs

- `text`: local terminal report.
- `json`: CI and scripts.
- `markdown`: PR comments and release notes.
- `mermaid`: graph of configured collection references.

## Exit Codes

- `0`: no findings at the selected threshold.
- `1`: findings met the selected threshold.
- `2`: CLI usage error.

