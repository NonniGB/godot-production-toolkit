# Godot CSV Guide

The first header cell must be `keys`:

```csv
keys,en,fr,es
MENU_START,Start,Demarrer,Iniciar
```

The guard checks:

- Duplicate keys.
- Empty required-language cells.
- UTF-8 BOM presence.
- Placeholder mismatches.
- Unchanged target strings.

Excel can introduce encoding and quoting surprises. Keep a tiny fixture in tests or CI if your localization workflow edits CSV files externally.
