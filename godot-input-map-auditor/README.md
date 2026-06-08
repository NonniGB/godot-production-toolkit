# Godot Input Map Auditor

Audit Godot input actions for keyboard, mouse, gamepad, and touch readiness, then generate input reference docs and strongly named GDScript constants.

This is a small CI-friendly tool for projects where input coverage can drift across desktop, controller, and mobile targets.

## Install

```powershell
python -m pip install -e .
```

When published:

```powershell
python -m pip install godot-input-map-auditor
```

## Quick Start

```powershell
godot-input-audit C:\Projects\MyGame --require keyboard,touch
godot-input-audit . --write-docs docs\INPUT_REFERENCE.md
godot-input-audit . --generate-gd scripts\generated\input_actions.gd
godot-input-audit . --format json --output input-report.json
```

Run against the sample project:

```powershell
godot-input-audit examples\tiny-godot-project --fail-on none
```

## What It Checks

- Parses the `[input]` section in `project.godot`.
- Classifies `InputEventKey`, mouse, joypad, and screen-touch event classes.
- Reports actions missing required device families.
- Reports duplicate normalized bindings across actions.
- Generates `INPUT_REFERENCE.md`.
- Generates optional `InputActions` GDScript constants.

## Documentation

- [Device classification](docs/DEVICE_RULES.md)
- [Rule reference](docs/RULE_REFERENCE.md)
- [Generated output](docs/GENERATED_OUTPUT.md)
- [Touch readiness](docs/TOUCH_READINESS.md)
- [CI usage](docs/CI.md)

## Development

```powershell
python -m pip install -e .
python -m unittest discover -s tests -v
godot-input-audit examples\tiny-godot-project --require keyboard --fail-on none
```

Examples and generated docs use generic action names so the repository can be published safely.
