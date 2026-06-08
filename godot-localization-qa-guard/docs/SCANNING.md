# Key Usage Scanning

Scan scripts:

```powershell
godot-l10n-guard . --translations translations --scan-scripts
```

Recognized script patterns:

- `tr("KEY")`
- `TranslationServer.translate("KEY")`

Scan scenes:

```powershell
godot-l10n-guard . --translations translations --scan-scenes
```

Scene scanning only picks up uppercase key-like `text = "MENU_TITLE"` values. This is intentionally conservative.
