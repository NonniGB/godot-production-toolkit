# Limitations

The first release is static and conservative:

- It does not execute Godot.
- It resolves target methods only when a scene node script is visible in the `.tscn` file.
- Dynamic `connect()` calls are only partially recognized.
- Built-in engine signals are not exhaustively validated.

Use the report as a drift detector, not a full substitute for runtime tests.
