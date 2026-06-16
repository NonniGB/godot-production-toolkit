# Godot Exporter Examples

These small Godot 4 scripts help a project write JSON inputs for Godot
Production Toolkit commands. Copy the scripts you need into a Godot project,
for example under `res://tools/toolkit_exporters/`, and keep the generated
files in a local `reports/` folder.

The examples are intentionally plain GDScript. They are starting points for
project-owned exporters, not a required runtime dependency.

## Mobile UI Metadata

Use `mobile_ui_metadata_exporter.gd` to inspect `Control` nodes in one scene and
write a `mobile-ui.json` file for `godot-mobile-ui-doctor`.

```powershell
godot --headless --path C:\Projects\MyGame --script res://tools/toolkit_exporters/mobile_ui_metadata_exporter.gd -- --scene res://ui/main_menu.tscn --output reports\mobile-ui.json --width 720 --height 1280 --safe-top 48 --safe-bottom 24
godot-mobile-ui-doctor reports\mobile-ui.json --format markdown --output reports\mobile-ui.md
godot-mobile-ui-doctor matrix reports\mobile-ui.json --format markdown --output reports\mobile-ui-matrix.md
```

If `--scene` is omitted, the exporter uses the project's configured main scene.

## Runtime Telemetry Snapshot

Use `runtime_telemetry_snapshot.gd` as an autoload or a child node in a smoke
test scene. It samples frame time, physics time, memory, node count, and draw
calls, then writes telemetry JSON for `godot-telemetry-lab`.

```powershell
godot --path C:\Projects\MyGame --scene res://tests/smoke_runtime.tscn
godot-telemetry-lab summarize reports\runtime --format markdown --output reports\runtime-summary.md
godot-telemetry-lab timeline reports\runtime --format html --output reports\runtime-timeline.html
```

Set the node's exported `output_path`, `scenario`, and `phase` values in the
Inspector or from your test runner.

## Scenario Result

Use `scenario_result_exporter.gd` when a simple Godot smoke runner needs to
write a scenario result JSON file for `godot-scenario-report`.

```powershell
godot --headless --path C:\Projects\MyGame --script res://tools/toolkit_exporters/scenario_result_exporter.gd -- --scenario menu_startup --status passed --duration-ms 910 --assertion "main menu visible:passed" --artifact screenshots/menu.png --output reports\scenarios\menu_startup.json
godot-scenario-report summarize reports\scenarios --format markdown --output reports\scenario-summary.md
```

Omit `--artifact` when the referenced screenshot, log, or trace file is not
written beside the result.

For manifest coverage, keep a project-owned `scenario-manifest.json` beside the
result folder and run:

```powershell
godot-scenario-report manifest coverage scenario-manifest.json --results reports\scenarios --format markdown --output reports\scenario-coverage.md
```

## Pack Manifest

Use `pack_manifest_exporter.gd` to scan selected `res://` files and write a
starter pack manifest for `godot-pack-mod-doctor`.

```powershell
godot --headless --path C:\Projects\MyGame --script res://tools/toolkit_exporters/pack_manifest_exporter.gd -- --id demo_patch --version 1.0.0 --output reports\pack-manifest.json --include .tscn,.tres,.gd,.png
godot-pack-mod-doctor check reports\pack-manifest.json --format markdown --output reports\pack.md
```

The generated manifest uses empty `references` arrays. Add project-specific
content ids there when your pack checker should verify references against a
base content manifest.

## Fixtures

The `fixtures/` folder contains tiny example outputs:

- `mobile-ui.json`
- `runtime-telemetry.json`
- `scenario-result.json`
- `pack-manifest.json`
