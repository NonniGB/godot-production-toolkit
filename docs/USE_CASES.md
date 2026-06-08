# Use Cases

Godot Production Toolkit is meant to sit beside normal unit tests, scene tests, and manual playtesting. It checks the release checks that are easy to forget until late in a build.

## Android Release Readiness

Use this before cutting an Android build:

```powershell
godot-project-doctor run --project . --checks export,mobile_perf,assets --reports-dir reports\godot-project-doctor --format markdown --output reports\godot-project-doctor\summary.md
```

This helps catch:

- Missing export paths.
- Empty Android package identifiers.
- Missing version codes or names.
- Debug export options left enabled.
- Mobile-unfriendly renderer and viewport settings.
- Oversized textures and risky import settings.

## Pixel-Art Asset Hygiene

Use this when adding or changing sprites, UI textures, tiles, or generated art:

```powershell
godot-asset-doctor . --profile pixel-2d --format json --output reports\assets.json
```

This helps catch:

- Mipmaps enabled on crisp pixel-art assets.
- Alpha-border fixing disabled on transparent assets.
- Transparent pixels with contaminated RGB values that can create edge fringes.
- Mobile texture memory risks.

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

## Automation And CI Workflows

Use JSON, SARIF, Markdown, and HTML outputs when another tool needs to read the result:

```powershell
godot-project-doctor run --project . --checks assets,export,input,mobile_perf --reports-dir reports\godot-project-doctor --format json --output reports\godot-project-doctor\summary.json
godot-project-doctor summarize reports\godot-project-doctor --format html --output reports\godot-project-doctor\summary.html
```

The individual tool commands remain visible in the plan output, so a maintainer can reproduce a failure without reverse-engineering the umbrella CLI.
