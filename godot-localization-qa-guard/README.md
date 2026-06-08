# Godot Localization QA Guard

A CI-friendly localization QA checker for Godot CSV and PO translation files. It catches missing strings, duplicate keys, broken placeholders, UTF-8 BOM issues, fuzzy PO entries, unchanged target strings, missing project keys, and unused catalog keys.

This is intentionally safe to publish as a standalone tool: examples are generic and the functionality does not reveal private game systems.

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
- `tr("KEY")` and `TranslationServer.translate("KEY")` usage.
- Uppercase key-like scene text values.
- Missing and unused keys when scanning is enabled.

## Documentation

- [Godot CSV guide](docs/CSV_GUIDE.md)
- [PO guide](docs/PO_GUIDE.md)
- [Placeholder checks](docs/PLACEHOLDERS.md)
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
