# Pseudo-Localization And Layout Checks

Pseudo-localization helps shake out UI problems before real translations arrive.
It keeps the original keys and source text, adds a pseudo locale column, accents
letters, preserves placeholders, and pads strings so compact layouts are easier
to spot.

```powershell
godot-l10n-guard . --translations translations --pseudo-output reports\pseudo-localized.csv --fail-on none
```

For a fuller UI stress pass, generate a stress pack:

```powershell
godot-l10n-guard stress-pack . --translations translations --output-dir reports\localization-stress --format markdown --output reports\localization-stress.md
```

The stress pack writes:

- `pseudo.csv`: accented pseudo-localized text with padding.
- `long.csv`: source text with heavier length padding for overflow checks.
- `compact.csv`: shortened text for narrow-label and icon-adjacent layouts.
- `rtl.csv`: right-to-left wrapped text for direction-sensitive layout checks.
- `stress-pack-manifest.json`: a machine-readable index of generated files.

The RTL-like output is a layout stress tool, not a correctness check for any
specific language. It helps find controls that assume left-to-right text before
real translation review begins.

## Use With Mobile UI Metadata

When a project also exports mobile UI rectangles, feed the generated manifest to
`godot-mobile-ui-doctor layout-risk`:

```powershell
godot-mobile-ui-doctor layout-risk mobile-ui.json --stress-pack reports\localization-stress\stress-pack-manifest.json --format markdown --output reports\mobile-layout-risk.md
```

The mobile UI report matches controls by `translation_key` when available and
falls back to visible source text when a key is not exported.

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
