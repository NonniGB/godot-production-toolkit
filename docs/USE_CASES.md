# Use Cases

Godot Production Toolkit is meant to sit beside normal unit tests, scene tests, and manual playtesting. It checks the release checks that are easy to forget until late in a build.

## Android Release Readiness

Use this before cutting an Android build:

```powershell
godot-project-doctor doctor . --profile release
godot-project-doctor run --project . --checks export,mobile_perf,assets --reports-dir reports\godot-project-doctor --format markdown --output reports\godot-project-doctor\summary.md
godot-export-doctor matrix . --expected-platform Android --expected-platform Web --format markdown --output reports\export-matrix.md
godot-export-doctor leaks . --format html --output reports\export-leaks.html --fail-on none
godot-export-doctor inspect-folder build\android --hash-files --format json --output reports\exported-folder.json --fail-on none
```

This helps catch:

- Missing export paths.
- Missing or duplicated expected export targets.
- Empty Android package identifiers.
- Missing version codes or names.
- Debug export options left enabled.
- Broad export filters that may include debug, test, temporary, or source-art files.
- Local-looking export paths or include filters before reports are shared.
- Exported folders or file lists containing development, backup, signing, or key files.
- Mobile-unfriendly renderer and viewport settings.
- Oversized textures and risky import settings.

## Pixel-Art Asset Hygiene

Use this when adding or changing sprites, UI textures, tiles, or generated art:

```powershell
godot-asset-doctor . --profile pixel-2d --format json --output reports\assets.json
```

Use this when sprites have hand-authored sockets, hardpoints, or UI markers:

```powershell
godot-asset-doctor manifest check sprite-manifest.json --project . --format json --output reports\sprite-manifest.json
```

This helps catch:

- Mipmaps enabled on crisp pixel-art assets.
- Alpha-border fixing disabled on transparent assets.
- Transparent pixels with contaminated RGB values that can create edge fringes.
- Mobile texture memory risks.
- Sprite manifest dimension mistakes and anchors outside the source PNG.

## Input Coverage For Touch And Desktop

Use this before merging control changes:

```powershell
godot-input-audit . --require keyboard,touch --format markdown --write-docs docs\input-map.md
```

This helps catch:

- Actions that work on keyboard but not touch.
- Actions that work on touch but not keyboard.
- Duplicate bindings that make UI prompts ambiguous.
- Missing generated input reference docs.

## Mobile UI Readiness

Use this after a project exports resolved UI rectangles from its menus, HUDs, or
touch screens:

```powershell
godot-mobile-ui-doctor mobile-ui.json --format markdown --output reports\mobile-ui.md
```

This helps catch:

- Touch targets that are too small.
- Controls placed too close together.
- Labels or buttons that overlap phone safe areas.
- Text that is likely to overflow after localization.
- UI rectangles that are partly off-screen.

## Localization QA

Use this before exporting a localized build:

```powershell
godot-l10n-guard . --translations translations --require fr,es --scan-scripts --format markdown --output reports\localization.md
```

This helps catch:

- Missing required language columns.
- Empty target strings.
- Placeholder mismatches, such as `{count}` versus `{total}`.
- Keys used by scripts but absent from translation files.
- Translation keys that are no longer used.

## Data-Driven Content Graphs

Use this before merging items, recipes, quests, dialogue, levels, enemies, or
content-pack files:

```powershell
godot-content-graph . --preset recipes --format markdown --output reports\content-graph.md --fail-on none
godot-content-graph . --preset recipes --changed-file data/items.json --format markdown --output reports\content-impact.md --fail-on none
```

This helps catch:

- Duplicate ids in content collections.
- References to ids that do not exist.
- Content that is no longer reachable from configured roots.
- Numeric outliers such as unusually high prices, cooldowns, weights, or build times.
- A Mermaid graph of configured content dependencies for review notes.

## Save Compatibility Checks

Use this when changing save-game data:

```powershell
godot-save-guard validate tests\fixtures\saves --schema schemas\save.schema.json --format markdown --output reports\saves.md
```

This helps catch:

- Missing required save fields.
- Type drift in saved values.
- Fixtures that no longer match the documented schema.
- Migration commands that need to be documented before release.

## Scene Signal Audits

Use this when scenes or autoloads are being refactored:

```powershell
godot-signal-audit . --format json --output reports\signals.json
```

This helps catch:

- Scene connections that target missing methods.
- Signal wiring that is hard to inspect manually.
- Autoload coupling that should be documented before it spreads.

## GDScript Architecture Checks

Use this when a project has feature folders, shared scripts, and autoloads that
need clear dependency direction:

```powershell
godot-architecture-guard . --config architecture-guard.toml --format sarif --output reports\architecture.sarif
```

This helps catch:

- Feature modules depending on folders they should not reach into.
- Scripts that use autoloads outside the module policy.
- `preload()` or `load()` paths that no longer exist.
- Dependency graphs that are useful during refactors.

## Scenario Evidence Reports

Use this after a scenario runner, smoke test, or custom harness emits JSON:

```powershell
godot-scenario-report summarize reports\scenarios --format html --output reports\scenarios\index.html
godot-scenario-report compare reports\baseline reports\current --format markdown --output reports\scenario-compare.md
godot-scenario-report manifest coverage scenario-manifest.json --results reports\scenarios --format html --output reports\scenario-coverage.html
godot-scenario-report flake compare reports\run-1 reports\run-2 reports\run-3 --format markdown --output reports\scenario-flakes.md
```

This helps catch:

- Failed scenarios and assertions.
- Missing listed artifacts such as screenshots.
- New failures compared with a baseline run.
- Duration regressions that make test runs or gameplay flows slower.
- Missing coverage for required tags, platforms, or critical flows.
- Scenarios whose status changes across repeated runs.

## Runtime Telemetry Evidence

Use this after a scenario runner, soak test, or debug exporter writes frame or
runtime samples:

```powershell
godot-telemetry-lab budget init --profile android-high --output reports\runtime-budget.json
godot-telemetry-lab summarize reports\runtime --format markdown --output reports\runtime.md
godot-telemetry-lab compare reports\baseline-runtime reports\current-runtime --format json --output reports\runtime-compare.json
godot-telemetry-lab timeline reports\runtime --budget-file reports\runtime-budget.json --format html --output reports\runtime-timeline.html
```

This helps catch:

- Frame p95 values above a selected budget.
- Runtime regressions compared with a saved baseline.
- Spikes in frame or memory samples across scenario phases.
- Scenario telemetry that needs a compact release-review artifact.

The input can be JSON or CSV. Common fields are `frame_ms`, `physics_ms`,
`memory_mb`, `nodes`, `draw_calls`, `scenario`, `phase`, and `time_s`.

## Pack, DLC, And Mod Manifests

Use this before publishing a patch, DLC, or mod/content pack manifest:

```powershell
godot-pack-mod-doctor manifest from-folder addons\demo_pack --id demo_pack --version 1.0.0 --output pack-manifest.json
godot-pack-mod-doctor check pack-manifest.json --base base-content.json --format markdown --output reports\pack.md
```

This helps catch:

- Missing pack identity fields.
- Duplicate shipped paths.
- Unexpected overrides.
- References to ids that are not present in a supplied base manifest.
- Local, parent-directory, or non-`res://` paths.
- Case-only path collisions that can break on Windows or macOS.
- Files that commonly need manual review before public pack distribution.

## Release Dashboards

Use this after individual checks have written JSON or Markdown reports:

```powershell
godot-release-dashboard build reports\godot-project-doctor --output reports\dashboard.html
```

This helps turn scattered release evidence into one static page for CI artifacts
or local review. The dashboard can include JSON summaries, Markdown notes, and
visual artifacts such as screenshot diffs, mobile UI overlays, and pixel-art
previews.

## Visual Smoke Checks

Use this for UI screens, menus, HUDs, and other stable rendered screens:

```powershell
godot-visual-smoke plan visual-smoke.toml --project . --format json
godot-visual-smoke compare baselines\menu.png screenshots\menu.png --diff reports\menu-diff.png
```

This helps catch:

- Blank or broken UI captures.
- Layout regressions.
- Unexpected pixel changes after rendering or theme updates.

## Script And CI Workflows

Use JSON, SARIF, Markdown, and HTML outputs when another tool needs to read the result:

```powershell
godot-project-doctor run --project . --checks assets,export,input,mobile_perf --reports-dir reports\godot-project-doctor --format json --output reports\godot-project-doctor\summary.json
godot-project-doctor summarize reports\godot-project-doctor --format html --output reports\godot-project-doctor\summary.html
```

The individual tool commands remain visible in the plan output, so a maintainer can reproduce a failure without reverse-engineering the umbrella CLI.

To keep one folder with the combined report index:

```powershell
godot-project-doctor collect godot-project-doctor.toml --evidence-dir reports\godot-project-doctor\evidence
```

This writes a manifest, Markdown/HTML summaries, and an artifact index for
screenshots, diffs, or scenario files listed by the individual reports.
