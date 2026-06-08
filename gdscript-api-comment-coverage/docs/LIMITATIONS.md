# Limitations

The first release uses a conservative line-based parser. It is designed for CI coverage gates, not perfect language understanding.

Known limits:

- Multiline function signatures are represented by their first line.
- Nested classes are not modeled separately.
- Comments must appear directly above the API item.
- Private methods beginning with `_` are intentionally skipped.

The rule of thumb: if the scanner cannot classify something confidently, it should stay quiet.
