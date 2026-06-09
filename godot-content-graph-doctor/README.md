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

Use a built-in preset when the project follows common data folder names:

```powershell
godot-content-graph path\to\godot-project --preset recipes
godot-content-graph path\to\godot-project --preset quests --preset dialogue --format markdown
```

See available presets:

```powershell
godot-content-graph . --list-presets
```

Write machine-readable output:

```powershell
godot-content-graph examples\tiny-content-project --config content-graph.toml --format json --output reports\content-graph.json
```

Create a Mermaid graph:

```powershell
godot-content-graph examples\tiny-content-project --config content-graph.toml --format mermaid --fail-on none
```

Show the collections touched by changed files and any downstream collections
that reference them:

```powershell
godot-content-graph path\to\godot-project --preset recipes --changed-file data/items.json --format markdown
```

## Config Example

Presets are useful for quick starts. A config file is still best when a project
uses custom paths, field names, or references. Config collections with the same
name as a preset collection override the preset.

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

## Built-In Presets

- `items`: `data/items.json` with common value, price, and weight summaries.
- `recipes`: `data/items.json` plus `data/recipes.json` input/output item references.
- `quests`: quest prerequisites and optional item rewards.
- `dialogue`: dialogue speaker and next-node references.
- `levels`: level references to item and enemy catalogs.
- `content-pack`: overlay item packs under `mods/content_pack/items.json`.

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

JSON, text, and Markdown reports include report metadata, plain-language rule
titles, and suggested fixes. JSON reports also include a `rules` object with
the rule explanations used by the current report.

Changed-file impact reports are included in `text`, `json`, and `markdown`
output when `--changed-file` or `--changed-files` is provided.

## Exit Codes

- `0`: no findings at the selected threshold.
- `1`: findings met the selected threshold.
- `2`: CLI usage error.
