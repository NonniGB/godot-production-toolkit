# Godot GDScript Architecture Guard

`godot-gdscript-architecture-guard` checks whether GDScript files still follow a
small architecture policy. It is aimed at projects where autoloads, shared
scripts, and feature modules can quietly become tangled during refactors.

It does not run the Godot editor. It scans `.gd` files and reports dependency
direction, autoload access, and unresolved `res://` script/resource references.

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

## Outputs

- `text`: local terminal report.
- `json`: CI and scripts.
- `markdown`: PR comments and review notes.
- `sarif`: GitHub code scanning.
- `mermaid`: dependency graph.

