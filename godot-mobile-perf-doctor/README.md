# Godot Mobile Perf Doctor

Static mobile performance diagnostics for Godot 4 projects, with optional parsing of captured adb summary text.

The first release deliberately starts with static checks so it works in CI without an Android device.

## Install

```powershell
python -m pip install -e .
```

When published:

```powershell
python -m pip install godot-mobile-perf-doctor
```

## Quick Start

```powershell
godot-mobile-perf-doctor C:\Projects\MyGame --static
godot-mobile-perf-doctor . --profile portrait-2d --format json --output perf-report.json
godot-mobile-perf-doctor . --adb-summary adb-summary.txt --format markdown --output mobile-perf-report.md
```

## What It Checks

- Renderer setting and mobile risk.
- Base viewport size.
- Stretch mode presence.
- PNG texture dimensions and estimated RGBA memory.
- Optional adb summary text for device model and janky frame counts.

## Documentation

- [Static checks](docs/STATIC_CHECKS.md)
- [Renderer guidance](docs/RENDERERS.md)
- [Texture guidance](docs/TEXTURES.md)
- [ADB summaries](docs/ADB.md)
- [Rule reference](docs/RULE_REFERENCE.md)
- [CI usage](docs/CI.md)

## Development

```powershell
python -m pip install -e .
python -m unittest discover -s tests -v
godot-mobile-perf-doctor examples\tiny-godot-project --static --fail-on none
```

Examples are generic and safe to publish.
