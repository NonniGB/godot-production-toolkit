# Godot Visual Smoke Test Kit

Screenshot diff and baseline helpers for Godot visual smoke tests. It reads scene/viewport config, compares PNG screenshots, writes diff images, approves baselines, and prints planned Godot capture commands.

The first release keeps Godot execution out of unit tests, so the package is easy to run in CI and safe to develop without a specific engine install.

## Install

```powershell
python -m pip install -e .
```

When published:

```powershell
python -m pip install godot-visual-smoke-test-kit
```

## Quick Start

```powershell
godot-visual-smoke plan visual-smoke.toml --project . --godot C:\Tools\Godot.exe
godot-visual-smoke plan visual-smoke.toml --project . --format json
godot-visual-smoke plan visual-smoke.toml --project . --viewport-manifest viewports.toml --format json
godot-visual-smoke compare baselines\menu.png current\menu.png --diff diffs\menu.png
godot-visual-smoke approve current\menu.png baselines\menu.png
godot-visual-smoke compare baselines\menu.png current\menu.png --format json --output visual-report.json
```

First successful path:

1. Run `plan` and capture current screenshots with your project-owned Godot helper.
2. Run `compare` with `--format json --output visual-report.json` and upload the current image, diff image, and JSON report as CI artifacts.
3. Review the current and diff images.
4. Run `approve` only for an intentional visual update.

If either the baseline or current screenshot is missing, `compare` returns a normal text or JSON finding that names the missing file and the next step.

## What It Does

- Parses `visual-smoke.toml`.
- Supports named viewport presets.
- Reuses viewport manifests across multiple smoke-test configs.
- Compares baseline and current PNG screenshots.
- Reports missing baseline or current screenshots with next-step guidance.
- Applies per-channel pixel tolerance.
- Fails when changed pixel percentage exceeds the configured threshold.
- Writes red diff images.
- Copies approved screenshots into baseline paths.
- Prints Godot capture commands for a project-owned helper script.
- Adds report metadata and readable failure explanations to JSON and text output.

## Documentation

- [Configuration](docs/CONFIGURATION.md)
- [Baseline workflow](docs/BASELINES.md)
- [Godot capture integration](docs/GODOT_CAPTURE.md)
- [CI usage](docs/CI.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## Development

```powershell
python -m pip install -e .
python -m unittest discover -s tests -v
godot-visual-smoke plan examples\visual-smoke.toml --project examples\tiny-godot-project
godot-visual-smoke compare baselines\menu.png current\menu.png --diff diffs\menu.png --format json --output visual-report.json
```

Examples are generic. Do not publish screenshots from private projects unless they have been reviewed.
