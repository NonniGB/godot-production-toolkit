# Contributing

Add tests before supporting new event types or rule behavior.

```powershell
python -m pip install -e .
python -m unittest discover -s tests -v
godot-input-audit examples\tiny-godot-project --fail-on none
```

Keep fixtures generic and minimal.
