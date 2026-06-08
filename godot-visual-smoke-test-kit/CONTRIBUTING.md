# Contributing

Add tests before changing diff behavior or config shape.

```powershell
python -m pip install -e .
python -m unittest discover -s tests -v
godot-visual-smoke plan examples\visual-smoke.toml --project examples\tiny-godot-project
```

Keep generated screenshots out of commits unless they are intentional baseline fixtures.
