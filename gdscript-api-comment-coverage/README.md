# GDScript API Comment Coverage

Generate a Markdown API index for Godot GDScript projects and enforce configurable comment coverage for public classes, signals, exported properties, constants, and public functions.

The goal is practical maintainability: a codebase-level map that can run in CI and catch undocumented public surfaces before they spread.

## Install

```powershell
python -m pip install -e .
```

When published:

```powershell
python -m pip install gdscript-api-comment-coverage
```

## Quick Start

```powershell
gdscript-api-coverage C:\Projects\MyGame --min-all 80
gdscript-api-coverage . --min-public-func 80 --min-signal 100
gdscript-api-coverage . --write-docs docs\API_INDEX.md
gdscript-api-coverage . --format json --output gdscript-api-report.json
```

Run against the sample:

```powershell
gdscript-api-coverage examples\tiny-godot-project --write-docs API_INDEX.md --fail-on none
```

## What It Finds

- `class_name` declarations.
- `signal` declarations.
- `@export var` properties, including annotation-on-previous-line style.
- Public `func` declarations that do not start with `_`.
- Public constants.
- Whether each item has an immediately preceding comment.

## Comment Style

Prefer Godot doc comments:

```gdscript
## Emitted when data changes.
signal data_changed(id: String)
```

Single `#` comments are accepted, but `##` is easier to distinguish as public documentation.

## Documentation

- [Comment conventions](docs/COMMENT_CONVENTIONS.md)
- [Thresholds](docs/CONFIGURATION.md)
- [Generated docs](docs/GENERATED_DOCS.md)
- [CI usage](docs/CI.md)
- [Limitations](docs/LIMITATIONS.md)

## Development

```powershell
python -m pip install -e .
python -m unittest discover -s tests -v
gdscript-api-coverage examples\tiny-godot-project --min-all 60 --write-docs API_INDEX.md
```

Examples and fixtures are generic and should not expose private project content.
