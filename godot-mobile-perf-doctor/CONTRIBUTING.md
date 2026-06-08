# Contributing

Add tests before changing rules or parser behavior.

```powershell
python -m pip install -e .
python -m unittest discover -s tests -v
godot-mobile-perf-doctor examples\tiny-godot-project --static --fail-on none
```

Keep diagnostics conservative and source-backed.
