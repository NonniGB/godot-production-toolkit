# Godot Mobile Perf Doctor

Static mobile performance diagnostics for Godot 4 projects, with optional parsing of captured adb summary text.

The first release deliberately starts with static checks so it works in CI without an Android device.

Use it before device testing to catch obvious mobile risks: desktop renderer settings, missing stretch configuration, oversized textures, and suspicious viewport settings.

## Install

```powershell
python -m pip install -e .
```

From PyPI:

```powershell
python -m pip install godot-mobile-perf-doctor
```

## Quick Start

```powershell
godot-mobile-perf-doctor C:\Projects\MyGame --static
godot-mobile-perf-doctor . --profile portrait-2d --format json --output perf-report.json
godot-mobile-perf-doctor . --adb-summary adb-summary.txt --format markdown --output mobile-perf-report.md
```

## Real Workflow: Prepare An Android Test Build

Run a static mobile scan before sending a build to a phone:

```powershell
godot-mobile-perf-doctor . --static --profile portrait-2d --fail-on warning --format markdown --output reports\mobile-perf.md
```

Use the report to check:

- whether the renderer choice is suitable for mobile;
- whether viewport and stretch settings are explicit;
- which PNG textures carry the largest estimated RGBA memory cost;
- whether a recent adb summary shows janky frames that need follow-up.

If you already captured a short device run, attach the summary:

```powershell
godot-mobile-perf-doctor . --adb-summary reports\adb-summary.txt --format json --output reports\mobile-perf.json
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

## CI Example

```yaml
- run: python -m pip install godot-mobile-perf-doctor
- run: godot-mobile-perf-doctor . --static --profile portrait-2d --format markdown --output reports/mobile-perf.md
```

## Development

```powershell
python -m pip install -e .
python -m unittest discover -s tests -v
godot-mobile-perf-doctor examples\tiny-godot-project --static --fail-on none
```

Examples are generic and safe to publish.
