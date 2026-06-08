# Contributing

Keep the tool focused on static release-readiness checks that can run before a Godot export.

## Development

```powershell
python -m pip install -e .
python -m unittest discover -s tests -v
godot-export-doctor examples\bad-export-project --fail-on none
```

## Rules

- Add a failing test before adding or changing a rule.
- Keep findings deterministic and redact secrets.
- Prefer conservative warnings over claims that require running Godot.
- Use generic fixtures. Do not include private project content.
