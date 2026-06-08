# Godot JSON Caveats

Save systems often drift when values cross boundaries between JSON, dictionaries, and UI text.

Common problems:

- Version stored as `"1"` instead of `1`.
- Currency, count, or resource values stored as strings.
- Missing version fields after early prototypes.
- Extra debug fields saved by development builds.

This tool is deliberately strict about numeric strings because they can break comparisons, migrations, or balancing logic later.
