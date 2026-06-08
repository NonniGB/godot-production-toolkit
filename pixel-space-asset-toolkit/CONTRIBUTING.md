# Contributing

Add deterministic tests before changing generator output.

```powershell
python -m pip install -e .
python -m unittest discover -s tests -v
pixel-space-assets starfield --width 64 --height 64 --seed 1 --stars 20 --output generated\starfield.png
```

Changing generator output is allowed, but document it in the changelog because seeds may no longer reproduce old assets.
