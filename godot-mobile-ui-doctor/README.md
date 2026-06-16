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

Render PNG overlays for quick visual review:

```powershell
godot-mobile-ui-doctor overlays mobile-ui.json --output-dir reports\mobile-ui-overlays --fail-on none
```

Combine the UI matrix with nearby mobile release reports:

```powershell
godot-mobile-ui-doctor readiness mobile-ui.json --input-report reports\input-map.json --export-report reports\export.json --mobile-perf-report reports\mobile-perf.json --format markdown --output reports\mobile-readiness.md
```

Reuse viewport definitions from a visual smoke capture plan:

```powershell
godot-visual-smoke plan visual-smoke.toml --project . --format json --output reports\visual-plan.json
godot-mobile-ui-doctor matrix mobile-ui.json --visual-smoke-plan reports\visual-plan.json --format markdown
godot-mobile-ui-doctor overlays mobile-ui.json --visual-smoke-plan reports\visual-plan.json --output-dir reports\mobile-ui-overlays
godot-mobile-ui-doctor readiness mobile-ui.json --visual-smoke-plan reports\visual-plan.json --visual-smoke-report reports\visual-plan.json --format markdown
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

If the UI metadata omits `viewports`, pass `--visual-smoke-plan` with JSON from
`godot-visual-smoke plan --format json`. Viewports in `mobile-ui.json` override
matching visual-smoke viewport names, so project-specific layout exports can
still take precedence.

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
- `png`: optional overlay previews from the `overlays` command.

JSON reports include the package version, a schema version, and a rule catalog.
Findings include stable `rule_id` values plus `rule_title` and `rule_help`
fields, so CI comments and local scripts can explain what to check next.

## Mobile Readiness Matrix

The `matrix` command groups findings by screen and viewport. It is useful when a
project has several phone and tablet captures and you want a quick table showing
which screens are clean, which need review, and which need action.

The matrix includes safe-area, touch-target, spacing, text-fit, and viewport
bounds status for each screen.

## Overlay Previews

The `overlays` command writes one PNG per screen and viewport. It draws the
safe-area rectangle, exported control bounds, interactive touch targets, and any
rule ids attached to a control. The output is useful for PR artifacts because a
reviewer can see the risky rectangles without opening the Godot project.

```powershell
godot-mobile-ui-doctor overlays mobile-ui.json --output-dir reports\mobile-ui-overlays --scale 0.5 --fail-on none
godot-mobile-ui-doctor overlays mobile-ui.json --screenshot-dir reports\screenshots --output-dir reports\mobile-ui-overlays --fail-on none
```

![Mobile UI overlay preview](docs/images/mobile-ui-overlays/main_menu__portrait_phone.png)

If `--screenshot-dir` is supplied, the command looks for PNGs named
`screen__viewport.png` or `screen.png` and draws the overlay on top of the
captured screen. Screens without a matching screenshot still use the plain grid
background.

## Combined Readiness

The `readiness` command builds on the screen matrix and can include JSON reports
from related toolkit checks:

- `--input-report` from `godot-input-audit`
- `--export-report` from `godot-export-doctor`
- `--localization-report` from `godot-l10n-guard`
- `--mobile-perf-report` from `godot-mobile-perf-doctor`
- `--visual-smoke-report` from `godot-visual-smoke`

This gives a compact mobile release review: portrait UI risks, touch/input
coverage, export settings, localization expansion risk, static mobile
performance warnings, and screenshot-plan status in one report. Linked reports
include their top findings so a reviewer can see the first actions without
opening every JSON file. Repeated rule ids are also grouped, which helps show
whether a linked report is failing because of one repeated setup problem or a
mix of unrelated issues.

## How To Export Metadata

The tool deliberately keeps the input format simple. A project-specific exporter
can walk visible `Control` nodes after layout and write each node's id, class,
global rectangle, visible text, font size, and whether it is interactive.

Good ids are stable names such as `cargo_buy_button` or `settings_back`, not
generated scene-instance paths. Stable ids make reports easier to compare across
runs.
