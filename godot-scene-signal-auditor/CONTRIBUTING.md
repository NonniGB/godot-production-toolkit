# Contributing

Add tests before expanding scene or GDScript parsing behavior.

```powershell
python -m pip install -e .
python -m unittest discover -s tests -v
godot-signal-audit examples\tiny-godot-project --format mermaid --fail-on none
```

Keep analysis conservative. If a connection cannot be resolved statically, the tool should avoid pretending it can.
