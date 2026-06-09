# Godot Mobile UI Doctor

`godot-mobile-ui-doctor` checks exported Godot UI metadata for common mobile
layout risks: small touch targets, cramped controls, safe-area overlap,
off-screen nodes, duplicate ids, and text that is likely to overflow its
rectangle.

The first version reads JSON metadata, so it can run in CI without opening the
Godot editor. Projects can generate the metadata from their own debug tools,
test harnesses, editor scripts, or screenshot pipelines.

## Install

```powershell
python -m pip install godot-mobile-ui-doctor
```

From a source checkout:

```powershell
python -m pip install -e .\godot-mobile-ui-doctor
```

## Quick Start

```powershell
godot-mobile-ui-doctor examples\tiny-mobile-ui-project\mobile-ui.json --format markdown
```

Fail CI when warnings are present:

```powershell
godot-mobile-ui-doctor mobile-ui.json --fail-on warning --format json --output reports\mobile-ui.json
```

Build a screen-by-screen readiness matrix:

```powershell
godot-mobile-ui-doctor matrix mobile-ui.json --format markdown --output reports\mobile-ui-matrix.md
```

## Metadata Shape

```json
{
  "thresholds": {
    "min_touch_size": 44,
    "min_touch_spacing": 8
  },
  "viewports": [
    {
      "name": "portrait_phone",
      "width": 720,
      "height": 1280,
      "safe_area": {"left": 0, "top": 48, "right": 0, "bottom": 24}
    }
  ],
  "screens": [
    {
      "name": "main_menu",
      "viewport": "portrait_phone",
      "nodes": [
        {
          "id": "play",
          "kind": "button",
          "x": 24,
          "y": 96,
          "width": 44,
          "height": 44,
          "text": "Play",
          "interactive": true
        }
      ]
    }
  ]
}
```

Coordinates are expected to be viewport pixels after layout. The tool does not
need scene files or a Godot binary for this first metadata-based check.

## Checks

- `missing_viewport`: a screen references a viewport that was not exported.
- `duplicate_node_id`: a screen repeats a node id.
- `node_outside_viewport`: a node rectangle leaves the viewport bounds.
- `safe_area_overlap`: an important node overlaps a safe-area inset.
- `touch_target_too_small`: an interactive node is smaller than the configured target size.
- `touch_targets_too_close`: interactive rectangles are too close together.
- `text_overflow_risk`: text is unlikely to fit in the exported rectangle.
- `no_interactive_controls`: a screen has no interactive controls in the metadata.

## Outputs

- `text`: readable terminal report.
- `json`: CI and scripts.
- `markdown`: PR comments, release notes, and report artifacts.

## Mobile Readiness Matrix

The `matrix` command groups findings by screen and viewport. It is useful when a
project has several phone and tablet captures and you want a quick table showing
which screens are clean, which need review, and which need action.

The matrix includes safe-area, touch-target, spacing, text-fit, and viewport
bounds status for each screen.

## How To Export Metadata

The tool deliberately keeps the input format simple. A project-specific exporter
can walk visible `Control` nodes after layout and write each node's id, class,
global rectangle, visible text, font size, and whether it is interactive.

Good ids are stable names such as `cargo_buy_button` or `settings_back`, not
generated scene-instance paths. Stable ids make reports easier to compare across
runs.
