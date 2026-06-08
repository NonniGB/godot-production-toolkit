# Contributing

Add tests before expanding schema support or migration behavior.

```powershell
python -m pip install -e .
python -m unittest discover -s tests -v
godot-save-guard validate examples\fixtures --schema examples\schema\save.schema.json --fail-on none
```

Keep save fixtures generic.
