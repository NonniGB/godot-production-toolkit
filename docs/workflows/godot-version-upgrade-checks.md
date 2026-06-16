# Godot Version Upgrade Checks

Use this workflow before and after moving a project between Godot 4.x versions.
The toolkit does not replace engine migration testing, but it can make common
drift easier to review: export presets, import settings, scene wiring, content
references, save fixtures, screenshots, and runtime evidence.

## Suggested Pass

Run the same checks before and after the engine upgrade, then compare reports:

```powershell
godot-project-doctor run --project . --checks assets,export,input,localization,signals,mobile_perf --reports-dir reports\before-upgrade --format json --output reports\before-upgrade\summary.json
godot-project-doctor run --project . --checks assets,export,input,localization,signals,mobile_perf --reports-dir reports\after-upgrade --format json --output reports\after-upgrade\summary.json
godot-project-doctor compare reports\before-upgrade reports\after-upgrade --format markdown --output reports\upgrade-compare.md --fail-on warning
```

For visual checks, compare screenshots captured from the old and new engine
versions:

```powershell
godot-visual-smoke compare screenshots\godot-4-old\main_menu.png screenshots\godot-4-new\main_menu.png --diff reports\upgrade-diffs\main_menu.png --format json --output reports\visual-upgrade.json
```

For content-heavy projects, add focused data checks:

```powershell
godot-content-graph . --preset recipes --format markdown --output reports\content-upgrade.md --fail-on none
godot-save-guard validate saves\fixtures --schema schemas\save.schema.json --format markdown --output reports\save-upgrade.md
```

## Keep As Evidence

- `upgrade-compare.md`: changed findings between the two runs.
- `visual-upgrade.json` and PNG diffs: visible rendering differences.
- `content-upgrade.md`: missing ids, duplicate ids, or unusual numeric changes.
- `save-upgrade.md`: save fixtures that still match the current schema.

## Review Notes

Expect some findings to be real migration work and some to be project-policy
choices. The useful part is making the differences visible in one place before
the upgrade branch is merged.
