# Godot HTML5 Web Export Checklist

Use this before publishing a Godot web build or changing an HTML5 export preset.
The checklist is meant for CI and local release prep: confirm the web preset is
present, make sure export paths are set, and collect nearby asset and input
reports that affect browser builds.

Related docs: [Tool Index](../TOOL_INDEX.md) and [Use Cases](../USE_CASES.md).

## Packages

- `godot-export-preset-doctor` for the web export preset.
- `godot-asset-pipeline-doctor` for texture and import settings.
- `godot-input-map-auditor` for keyboard, mouse, touch, and controller coverage.
- `godot-project-doctor` when these checks should run together.

## Copy-paste commands

```powershell
python -m pip install godot-export-preset-doctor godot-asset-pipeline-doctor godot-input-map-auditor
godot-export-doctor . --platform Web --format json --output reports\web-export.json
godot-export-doctor inspect-folder build\web --format markdown --output reports\web-exported-folder.md --fail-on none
godot-asset-doctor . --profile web --format markdown --output reports\web-assets.md
godot-input-audit . --format markdown --output reports\web-input.md
```

If the project uses a combined report:

```powershell
godot-export-doctor . --platform Web --format markdown --output reports\web-export.md
godot-asset-doctor . --profile pixel-2d --format json --output reports\web-assets.json --fail-on none
godot-input-audit . --format markdown --output reports\web-input.md --fail-on none
```

## Expected inputs

- A Godot project root containing `project.godot`.
- `export_presets.cfg` with a Web or HTML5 preset.
- Asset import metadata and input actions from the project.

## Expected outputs

- A web export report in JSON, SARIF, or Markdown.
- Asset and input reports that can be attached to a CI job.
- A failing exit code only when findings reach the selected threshold.
