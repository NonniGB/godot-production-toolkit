# Contributing

## Local Setup

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -e .
.\.venv\Scripts\python -m unittest discover -s tests -v
```

## Development Rules

- Keep checks deterministic and explainable.
- Prefer warning-level checks unless an issue is likely to break import, export, or runtime behavior.
- Add a fixture test for every new rule.
- Keep public examples generic. Do not include proprietary game data or project-specific assets.
- Do not require a Godot binary for the core scan path.

## Release Checklist

1. Run `python -m unittest discover -s tests -v`.
2. Run `python -m godot_asset_doctor examples/tiny-godot-project --fail-on none`.
3. Update `CHANGELOG.md`.
4. Tag the release.
5. Build the package with `python -m build` when the `build` package is available.

