# Contributing

This project intentionally starts with a conservative line-based parser. Add tests before expanding syntax support.

## Development

```powershell
python -m pip install -e .
python -m unittest discover -s tests -v
gdscript-api-coverage examples\tiny-godot-project --write-docs API_INDEX.md --fail-on none
```

Guidelines:

- Keep generated output deterministic.
- Prefer false negatives over noisy false positives.
- Do not include private project scripts in fixtures.
