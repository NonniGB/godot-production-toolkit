# Godot GDScript Architecture Guard

`godot-gdscript-architecture-guard` checks whether GDScript files still follow a
small architecture policy. It is aimed at projects where autoloads, shared
scripts, and feature modules can quietly become tangled during refactors.

It does not run the Godot editor. It scans `.gd` files and reports dependency
direction, autoload access, unresolved `res://` script/resource references,
module owner summaries, high fan-in/fan-out from visible script references, and
possible unused scripts/resources.

## Install

```powershell
python -m pip install godot-gdscript-architecture-guard
```

From a source checkout:

```powershell
python -m pip install -e .\godot-gdscript-architecture-guard
```

## Quick Start

```powershell
godot-architecture-guard examples\tiny-architecture-project --config architecture-guard.toml
```

Write SARIF for code scanning:

```powershell
godot-architecture-guard . --config architecture-guard.toml --format sarif --output reports\architecture.sarif
```

Write a Markdown refactor note:

```powershell
godot-architecture-guard . --config architecture-guard.toml --format markdown --output reports\architecture.md --fail-on none
```

## Policy Example

```toml
[modules.ui]
paths = ["scripts/ui/**"]
may_depend_on = ["shared"]
allowed_autoloads = ["Settings"]

[modules.gameplay]
paths = ["scripts/gameplay/**"]
may_depend_on = ["shared"]
allowed_autoloads = ["GameState"]

[modules.shared]
paths = ["scripts/shared/**"]
may_depend_on = []
allowed_autoloads = []

[autoloads]
names = ["GameState", "Settings"]
```

If `scripts/ui/menu.gd` preloads `res://scripts/gameplay/inventory.gd`, the tool
reports a module boundary violation unless `ui` may depend on `gameplay`.

If a configured module path matches no scripts, the tool reports that stale
policy path as a warning. JSON, text, and Markdown reports also include advisory
sections for module ownership, files with many visible script references, and
scripts or resources that do not appear in visible `res://` references.
Script checks also treat `class_name` declarations as public entry points.

## Outputs

- `text`: local terminal report.
- `json`: CI and scripts.
- `markdown`: PR comments and review notes.
- `sarif`: GitHub code scanning.
- `mermaid`: dependency graph.

JSON reports include `metadata`, `rule_help`, and per-finding suggestions so CI
jobs and small review scripts can explain the issue without hard-coding rule
text. They also include `owner_summaries`, `hotspots`, and
`possible_unused_scripts` / `possible_unused_resources` arrays for refactor
review.
SARIF output carries rule descriptions for code scanning tools.
