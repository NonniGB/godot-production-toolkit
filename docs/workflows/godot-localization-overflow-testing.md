# Godot Localization Overflow Testing

Use this when translated text, pseudo-localized strings, or long UI labels might
overflow buttons, menus, HUD panels, or mobile layouts. It is useful before
importing a new language, changing fonts, or approving portrait-first UI.

Related docs: [Tool Index](../TOOL_INDEX.md) and [Use Cases](../USE_CASES.md).

## Packages

- `godot-localization-qa-guard` for CSV/PO placeholder, key, glyph, and
  pseudo-localization checks.
- `godot-mobile-ui-doctor` for exported UI rectangles, touch targets, safe
  areas, and text-fit metadata.
- `godot-visual-smoke-test-kit` when the project also captures screenshots for
  visual comparison.

## Copy-paste commands

```powershell
python -m pip install godot-localization-qa-guard godot-mobile-ui-doctor godot-visual-smoke-test-kit
godot-l10n-guard . --format markdown --output reports\localization.md
godot-l10n-guard pseudo translations\en.csv --output reports\pseudo-en.csv
godot-mobile-ui-doctor readiness mobile-ui.json --localization-report reports\localization.json --format markdown --output reports\mobile-localization-readiness.md
```

For screenshot-backed review, capture your project-owned UI screenshots first,
then compare them with the visual smoke tool:

```powershell
godot-visual-smoke compare baselines\ui current\ui --format json --output reports\ui-visual-diff.json --fail-on-diff
```

## Expected inputs

- Localization files such as `*.csv`, `*.po`, or `*.pot`.
- Exported UI metadata such as `mobile-ui.json`.
- Optional screenshot folders from a project-owned capture command.
- Optional font or glyph allow-list configuration.

## Expected outputs

- Localization QA reports with placeholder, key, expansion, and glyph findings.
- Mobile UI readiness reports that can be reviewed in Markdown or JSON.
- Optional screenshot diff reports for UI states that need visual approval.
