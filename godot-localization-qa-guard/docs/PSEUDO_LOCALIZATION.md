# Pseudo-Localization And Layout Checks

Pseudo-localization helps shake out UI problems before real translations arrive.
It keeps the original keys and source text, adds a pseudo locale column, accents
letters, preserves placeholders, and pads strings so compact layouts are easier
to spot.

```powershell
godot-l10n-guard . --translations translations --pseudo-output reports\pseudo-localized.csv --fail-on none
```

Use a custom pseudo locale name when your project has a naming convention:

```powershell
godot-l10n-guard . --translations translations --pseudo-locale zz --pseudo-output reports\pseudo.csv --fail-on none
```

Expansion checks warn when a translated string is much longer than the source:

```powershell
godot-l10n-guard . --translations translations --max-expansion 1.35
```

Glyph checks are a simple font-readiness guard. Put the characters your UI font
is expected to cover in a text file, then run:

```powershell
godot-l10n-guard . --translations translations --allowed-glyphs-file fonts\ui-glyphs.txt
```

You can also pass a short allow-list directly:

```powershell
godot-l10n-guard . --translations translations --allowed-glyphs "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 .,!?-"
```

These checks are intentionally opt-in. They are most useful once your UI has
stable font choices, known touch targets, or narrow panels that are sensitive to
long translated strings.
