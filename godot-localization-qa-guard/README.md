# Godot Localization QA Guard

A CI-friendly localization QA checker for Godot CSV and PO translation files. It catches missing strings, duplicate keys, broken placeholders, UTF-8 BOM issues, fuzzy PO entries, unchanged target strings, missing project keys, unused catalog keys, and layout-sensitive text risks.

## Install

```powershell
python -m pip install -e .
```

When published:

```powershell
python -m pip install godot-localization-qa-guard
```

## Quick Start

```powershell
godot-l10n-guard C:\Projects\MyGame --translations translations --require fr,es
godot-l10n-guard . --csv assets\i18n\strings.csv --scan-scripts --scan-scenes
godot-l10n-guard . --po locale --format markdown --output docs\LOCALIZATION_QA.md
godot-l10n-guard . --format json --output localization-report.json
godot-l10n-guard . --translations translations --max-expansion 1.35 --allowed-glyphs-file fonts\ui-glyphs.txt
godot-l10n-guard . --translations translations --pseudo-output reports\pseudo-localized.csv --fail-on none
godot-l10n-guard stress-pack . --translations translations --output-dir reports\localization-stress --format markdown --output reports\localization-stress.md
godot-l10n-guard capture-plan . --stress-pack reports\localization-stress\stress-pack-manifest.json --screen main_menu --screen settings --viewport portrait_phone --format markdown --output reports\localization-capture-plan.md
godot-mobile-ui-doctor layout-risk mobile-ui.json --stress-pack reports\localization-stress\stress-pack-manifest.json --format markdown --output reports\mobile-layout-risk.md
```

Run the sample:

```powershell
godot-l10n-guard examples\tiny-godot-project --translations examples\tiny-godot-project\translations --scan-scripts --fail-on none
```

## What It Checks

- Godot CSV header starts with `keys`.
- Required language columns exist.
- Required target cells are not empty.
- Duplicate CSV keys and PO `msgid` values.
- PO fuzzy and untranslated entries.
- Placeholder sets match across source and target text.
- Target strings that are unchanged from source.
- Target strings that exceed an optional expansion ratio.
- Characters outside an optional UI-font glyph allow-list.
- `tr("KEY")` and `TranslationServer.translate("KEY")` usage.
- Uppercase key-like scene text values.
- Missing and unused keys when scanning is enabled.
- Pseudo-localized CSV previews for UI stress testing.
- Synthetic pseudo, long, compact, and RTL-like CSV catalogs for layout review.
- Screenshot capture plans for stress locales, screens, and viewport profiles.
- Report metadata and plain-language rule explanations for easier CI review.

## Documentation

- [Godot CSV guide](docs/CSV_GUIDE.md)
- [PO guide](docs/PO_GUIDE.md)
- [Placeholder checks](docs/PLACEHOLDERS.md)
- [Pseudo-localization and layout checks](docs/PSEUDO_LOCALIZATION.md)
- [Key usage scanning](docs/SCANNING.md)
- [Rule reference](docs/RULE_REFERENCE.md)
- [CI usage](docs/CI.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## Development

```powershell
python -m pip install -e .
python -m unittest discover -s tests -v
godot-l10n-guard examples\tiny-godot-project --translations examples\tiny-godot-project\translations --scan-scripts --fail-on none
```
