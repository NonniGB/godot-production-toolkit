# Contributing

Add tests before expanding parser behavior or rule coverage.

```powershell
python -m pip install -e .
python -m unittest discover -s tests -v
godot-l10n-guard examples\tiny-godot-project --translations examples\tiny-godot-project\translations --scan-scripts --fail-on none
```

Keep sample strings generic and avoid private project text.
