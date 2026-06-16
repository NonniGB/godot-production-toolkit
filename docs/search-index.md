# Workflow Finder

Use this page when you know the production problem you are trying to solve, but
not the package name yet. The entries use practical phrases people search for
during Godot release work and point to the most relevant workflow pages, package
docs, CI recipes, and sample reports.

## Export And Platform Builds

### "My Godot export preset keeps breaking CI"

Start with the [Android export CI workflow](workflows/godot-android-export-ci.md)
and the [`godot-export-preset-doctor` README](../godot-export-preset-doctor/README.md).
For GitHub Actions, compare your workflow with the
[Android export recipe](ci/android-export.yml) and the
[`godot-ci-doctor-action` README](../godot-ci-doctor-action/README.md).

The export doctor is the first check for missing export paths, debug flags,
version fields, package identifiers, local-looking paths, broad export filters,
and preset drift. Use `godot-export-doctor matrix` when you want a release
target matrix for Android, web, desktop, or console-adjacent preset reviews. If
the export report will feed a broader release page, see the
[report gallery](report-gallery/README.md) for the release readiness sample.

### "A release target is missing from export_presets.cfg"

Use `godot-export-doctor matrix` with the platforms your CI expects:

```powershell
godot-export-doctor matrix . --expected-platform Android --expected-platform Web --format markdown
```

This helps spot missing or duplicated export targets before a release workflow
selects the wrong preset.

### "I need Android export checks before shipping"

Use the [Android release workflow](workflows/godot-android-export-ci.md),
[`godot-export-preset-doctor`](../godot-export-preset-doctor/README.md), and
[`godot-mobile-perf-doctor`](../godot-mobile-perf-doctor/README.md) together.
The [copy-paste Android CI recipe](ci/android-export.yml) shows how to run the
export check, build the Android export, and upload reports.

If art or import settings are part of the risk, add
[`godot-asset-pipeline-doctor`](../godot-asset-pipeline-doctor/README.md). The
[release readiness gallery entry](report-gallery/README.md#umbrella-report-inputs)
shows Android export, input, asset, and mobile performance reports used together.

Use `godot-export-doctor leaks` when a report needs to show whether broad export
filters could include debug scenes, test folders, source-art files, temporary
files, or local workstation paths.

### "I need HTML5 or web export checks"

Start with the [HTML5 web export checklist](workflows/godot-html5-web-export-checklist.md)
and the [HTML5 CI recipe](ci/html5-export.yml). Use
[`godot-export-preset-doctor`](../godot-export-preset-doctor/README.md) for the
web preset itself, then add
[`godot-visual-smoke-test-kit`](../godot-visual-smoke-test-kit/README.md) when a
browser build needs screenshot evidence.

## UI, Localization, And Screenshots

### "My phone UI might overlap the notch or system bars"

Use the [mobile safe-area workflow](workflows/godot-mobile-ui-safe-area-testing.md)
and [`godot-mobile-ui-doctor`](../godot-mobile-ui-doctor/README.md). The mobile
UI doctor checks exported control rectangles, safe areas, touch targets, spacing,
and overlay previews.

For CI, the [mobile UI and localization recipe](ci/mobile-ui-and-localization.yml)
shows the safe-area and text checks running together. The
[mobile UI gallery entry](report-gallery/README.md#start-here) links to sample
layout reports, a readiness matrix, and screenshots.

### "Translated text may overflow buttons or menus"

Start with the [localization overflow workflow](workflows/godot-localization-overflow-testing.md).
Use [`godot-localization-qa-guard`](../godot-localization-qa-guard/README.md) for
translation files and script key usage, then use
[`godot-mobile-ui-doctor`](../godot-mobile-ui-doctor/README.md) for exported UI
rectangles, text lengths, and safe-area layout.

The [mobile UI and localization CI recipe](ci/mobile-ui-and-localization.yml)
is the best copy point when both translation quality and visible layout fit
matter in the same review.

### "I need visual regression testing for scenes, menus, or HUDs"

Use the [visual regression workflow](workflows/godot-visual-regression-testing.md)
and [`godot-visual-smoke-test-kit`](../godot-visual-smoke-test-kit/README.md).
It covers screenshot planning, baseline comparison, diff artifacts, and approval
flows for stable screens.

When screenshot diffs should be part of a larger release artifact, pair it with
[`godot-release-dashboard-kit`](../godot-release-dashboard-kit/README.md) and
the [release dashboard CI recipe](ci/release-dashboard-artifact.yml).

## Data, Saves, And Content Packs

### "Save data changed and I need migration testing"

Use the [save migration workflow](workflows/godot-save-migration-testing.md) and
[`godot-save-schema-guard`](../godot-save-schema-guard/README.md). The save guard
validates fixtures against a schema and helps document migration commands before
a release.

For a broader production pass, add the umbrella
[`godot-project-doctor`](../godot-project-doctor/README.md) so save evidence can
sit beside export, asset, input, and localization reports.

### "A content pack, DLC, mod, or patch manifest needs validation"

Start with the [mod and DLC pack workflow](workflows/godot-mod-dlc-pack-validation.md)
and [`godot-pack-mod-doctor`](../godot-pack-mod-doctor/README.md). It checks pack
identity, shipped paths, overrides, dependencies, and references against an
optional base manifest.

If the pack also changes items, recipes, levels, quests, or other data-driven
content, run [`godot-content-graph-doctor`](../godot-content-graph-doctor/README.md)
as well. The [content pack CI recipe](ci/content-pack-validation.yml) shows both
checks in one workflow.

### "Data files reference missing items, quests, recipes, or levels"

Use [`godot-content-graph-doctor`](../godot-content-graph-doctor/README.md) for
content graph validation. It finds duplicate IDs, missing references, unreachable
content, and numeric outliers in data-driven projects.

The [content graph sample](report-gallery/README.md#start-here) links to a tiny
fixture, Markdown report, terminal screenshot, and regeneration command.

## Code, Architecture, And Inputs

### "A GDScript refactor might break architecture boundaries"

Use [`godot-gdscript-architecture-guard`](../godot-gdscript-architecture-guard/README.md)
for GDScript architecture and refactor safety checks. It helps review module
dependencies, autoload access, missing load paths, and dependency graphs.

If the refactor touches scene wiring, add
[`godot-scene-signal-auditor`](../godot-scene-signal-auditor/README.md). The
[architecture guard gallery sample](report-gallery/README.md#start-here) shows
the kind of report a reviewer can inspect without opening the whole project.

### "Controls work on keyboard but not touch, mouse, or controller"

Use [`godot-input-map-auditor`](../godot-input-map-auditor/README.md) for input
map coverage. It checks required device families, duplicate bindings, missing
actions, and generated input docs.

For mobile work, pair it with
[`godot-mobile-ui-doctor`](../godot-mobile-ui-doctor/README.md) so action
coverage and touch layout are reviewed together. The release readiness sample in
the [report gallery](report-gallery/README.md#umbrella-report-inputs) includes
an input map report.

## Runtime Evidence And Release Review

### "Will a Godot 4.x upgrade break my project?"

Use the [Godot version upgrade workflow](workflows/godot-version-upgrade-checks.md).
It suggests running the same export, asset, input, localization, signal, mobile
performance, visual smoke, content graph, and save fixture checks before and
after the engine upgrade.

Keep the before/after reports and screenshot diffs together so review focuses
on changed findings rather than re-reading every report from scratch.

### "Scenario runs need reviewable evidence"

Use [`godot-scenario-report-kit`](../godot-scenario-report-kit/README.md) for
scenario evidence, manifest coverage, flake comparison, baseline comparison, and
HTML summaries. It is designed for JSON output from scenario runners, smoke
tests, or custom harnesses.

The [scenario gallery entries](report-gallery/README.md#start-here) show
comparison reports, coverage HTML, screenshots, fixtures, and commands used to
regenerate the examples.

### "Runtime telemetry needs a budget or timeline"

Use the [runtime performance regression workflow](workflows/godot-runtime-performance-regression.md)
and [`godot-runtime-telemetry-lab`](../godot-runtime-telemetry-lab/README.md).
It turns frame, memory, draw-call, node-count, scenario, and phase samples into
summaries, budget checks, baseline comparisons, and HTML timelines.

For CI, start with the [runtime telemetry budget recipe](ci/runtime-telemetry-budget.yml).
The [runtime telemetry gallery sample](report-gallery/README.md#start-here)
shows the timeline report and screenshot.

### "Several reports need one release dashboard"

Use [`godot-release-dashboard-kit`](../godot-release-dashboard-kit/README.md) to
turn JSON, Markdown, screenshots, overlays, diffs, and telemetry artifacts into
one static HTML dashboard. The [release dashboard CI recipe](ci/release-dashboard-artifact.yml)
shows how to publish it as a workflow artifact.

The [report gallery](report-gallery/README.md) includes a dashboard demo, sample
HTML, screenshot, fixture, and regeneration command.

## Assets And Pixel Art

### "Pixel art imports, icons, or sprite anchors need checks"

Use [`godot-asset-pipeline-doctor`](../godot-asset-pipeline-doctor/README.md)
for pixel art asset checks, Godot `.import` settings, texture memory risks,
icons, audio, and sprite manifest validation.

If you need deterministic space-themed preview sheets or PNG image diffs, use
[`pixel-space-asset-toolkit`](../pixel-space-asset-toolkit/README.md). The
[sprite manifest gallery entry](report-gallery/README.md#start-here) links to a
sample text report and the asset-doctor image examples.

## Broader Maps

- [Tool index](TOOL_INDEX.md): concise tool-to-command table.
- [Use cases](USE_CASES.md): longer examples by release activity.
- [Workflow pages](workflows/): task-specific checklists.
- [CI recipes](ci/README.md): copy-paste GitHub Actions examples.
- [Report gallery](report-gallery/README.md): sample reports, screenshots, and
  fixtures.
